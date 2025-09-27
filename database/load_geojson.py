"""
загрузка границ субъектов рф из russia.geojson в region.geom (multipolygon, 4326).
поддержка ручной карты соответствий (region_name_map.json) и вспомогательных вариантов из cities.geojson.
требуется: psycopg2-binary
"""

import json
import os
import re
import unicodedata
from typing import Dict, Tuple, Optional

import psycopg2
from config_base import DB, RUSSIA_GEOJSON, CITIES_GEOJSON

MAP_FILE = "region_name_map.json"
SUGGEST_FILE = "region_name_map_suggest.json"

REGION_NAME_KEYS = [
    "name",
    "NAME",
    "name_ru",
    "NAME_RU",
    "name_rus",
    "NAME_RUS",
    "region",
    "subject",
    "subj",
    "adm1_name",
    "adm1",
    "oblast",
    "krai",
    "NAME_1",
    "NAME_LONG",
    "REGION",
    "SUBJECT",
    "REGION_NAME",
    "ADM1NAME",
]
CITY_REGION_KEYS = [
    "region",
    "region_name",
    "subject",
    "reg_name",
    "adm1_name",
    "adm1",
    "subj",
    "oblast",
    "krai",
    "federal_subject",
]


def _norm_base(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).strip().lower()
    s = s.replace("ё", "е")
    return re.sub(r"\s+", " ", s)


def _strip_admin_words(s: str) -> str:
    s = re.sub(r"\(.*?\)", "", s)
    for p in [
        r"\bреспублика\b",
        r"\bобласть\b",
        r"\bкрай\b",
        r"\bгород\b",
        r"\bг\.\b",
        r"\bавтономный округ\b",
        r"\bавтономный\b",
        r"\bокруг\b",
        r"\bао\b",
        r"\bчувашская\b",
        r"\bресп\.\b",
    ]:
        s = re.sub(p, "", s)
    s = re.sub(r"[«»\"'.,]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _norm_name(s: str) -> str:
    return _strip_admin_words(_norm_base(s))


def _get_prop(props: dict, keys: list) -> Optional[str]:
    for k in keys:
        if k in props and props[k]:
            return str(props[k])
    for v in props.values():
        if isinstance(v, str) and v.strip():
            return v
    return None


def _load_geojson(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _connect():
    return psycopg2.connect(
        host=DB["host"],
        port=DB["port"],
        dbname=DB["dbname"],
        user=DB["user"],
        password=DB["password"],
    )


def _build_region_index(cur) -> Dict[str, Tuple[int, str]]:
    cur.execute("select id, name from region;")
    idx: Dict[str, Tuple[int, str]] = {}
    for rid, name in cur.fetchall():
        if not name:
            continue
        idx[_norm_base(name)] = (rid, name)
        idx[_norm_name(name)] = (rid, name)
    return idx


def _build_city_variants() -> Dict[str, str]:
    if not CITIES_GEOJSON or not os.path.exists(CITIES_GEOJSON):
        return {}
    gj = _load_geojson(CITIES_GEOJSON)
    variants = set()
    for f in gj.get("features", []):
        props = f.get("properties", {}) or {}
        reg = _get_prop(props, CITY_REGION_KEYS)
        if reg:
            variants.add(_norm_base(reg))
            variants.add(_norm_name(reg))
    return {v: v for v in variants}


if __name__ == "__main__":
    if not os.path.exists(RUSSIA_GEOJSON):
        raise FileNotFoundError(f"не найден файл: {RUSSIA_GEOJSON}")

    gj = _load_geojson(RUSSIA_GEOJSON)
    features = gj.get("features", [])

    name_map = {}
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
            name_map = {_norm_name(k): v for k, v in raw.items()}

    city_variants = _build_city_variants()

    conn = _connect()
    conn.autocommit = False
    cur = conn.cursor()

    region_index = _build_region_index(cur)

    total = matched = updated = 0
    not_found = []

    for feat in features:
        total += 1
        props = feat.get("properties", {}) or {}
        geom = feat.get("geometry")
        if not geom:
            continue

        raw_name = _get_prop(props, REGION_NAME_KEYS)
        if not raw_name:
            continue

        n_full = _norm_base(raw_name)
        n_clean = _norm_name(raw_name)

        target = region_index.get(n_full) or region_index.get(n_clean)

        if not target and n_clean in name_map:
            m = name_map[n_clean]
            target = region_index.get(_norm_name(m)) or region_index.get(_norm_base(m))

        if not target and n_clean in city_variants:
            target = region_index.get(n_clean)

        if not target:
            for key in region_index.keys():
                if key.startswith(n_clean) or n_clean.startswith(key):
                    target = region_index[key]
                    break

        if not target:
            not_found.append(raw_name)
            continue

        region_id, _ = target
        matched += 1

        gjson = json.dumps(geom, ensure_ascii=False)
        cur.execute(
            """
            with g as (
              select ST_SetSRID(
                       ST_Multi(
                         ST_CollectionExtract(
                           ST_MakeValid(ST_GeomFromGeoJSON(%s)), 3
                         )
                       ), 4326
                     ) as geom
            )
            update region r
               set geom = g.geom
              from g
             where r.id = %s
               and not ST_IsEmpty(g.geom)
               and (r.geom is distinct from g.geom);
            """,
            (gjson, region_id),
        )
        if cur.rowcount > 0:
            updated += 1

    conn.commit()
    cur.close()
    conn.close()

    print("готово.")
    print(f"фич в geojson: {total}")
    print(f"совпало по имени: {matched}")
    print(f"обновлено geom: {updated}")

    if not_found:
        with open(SUGGEST_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {n: "" for n in sorted(set(not_found))}, f, ensure_ascii=False, indent=2
            )
        print(f"создан файл подсказок: {SUGGEST_FILE}")
