# pip install pandas psycopg2-binary openpyxl

import math
import datetime as dt
import os
import pandas as pd
import psycopg2
from database.config_base import *

_dsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@skeleton_restore-db-1:5432/droneradar")


def _conn():
    return psycopg2.connect(_dsn)


def _to_int_safe(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    try:
        return int(x)
    except Exception:
        return None


def _parse_time_like(t):
    if t is None or pd.isna(t):
        return None
    if isinstance(t, pd.Timestamp):
        return t.time()
    if isinstance(t, str):
        try:
            parts = [int(p) for p in t.split(":")]
            while len(parts) < 3:
                parts.append(0)
            return dt.time(parts[0], parts[1], parts[2])
        except Exception:
            return None
    if isinstance(t, (float, int)):
        sec = int(float(t) * 24 * 3600)
        h, m = divmod(sec, 3600)
        m, s = divmod(m, 60)
        return dt.time(h % 24, m, s)
    return None


def _to_py_date(d):
    if d is None or pd.isna(d):
        return None
    if isinstance(d, pd.Timestamp):
        return d.date()
    if isinstance(d, dt.date):
        return d
    if isinstance(d, str):
        try:
            return pd.to_datetime(d, errors="coerce").date()
        except Exception:
            return None
    return None


def _combine_ts(dep_date, dep_time):
    d = _to_py_date(dep_date)
    t = _parse_time_like(dep_time)
    if d is None and t is None:
        return None
    if d is None:
        d = dt.date.today()
    if t is None:
        t = dt.time(0, 0, 0)
    return dt.datetime.combine(d, t)


def _first_day_of_month(d):
    if isinstance(d, dt.datetime):
        d = d.date()
    return dt.date(d.year, d.month, 1)


def _is_number(x):
    return x is not None and not (isinstance(x, float) and math.isnan(x))


def _none_if_nat(x):
    if x is None or pd.isna(x):
        return None
    if isinstance(x, pd.Timestamp):
        return x.to_pydatetime()
    return x


SQL_UPSERT_REGION = """
insert into region(name) values (%s)
on conflict (name) do update set name = excluded.name
returning id;
"""

SQL_UPSERT_UAV = """
insert into uav_type(code) values (%s)
on conflict (code) do update set code = excluded.code
returning id;
"""

SQL_UPSERT_REGION_STATS = """
insert into region_stats(region_id, valid_from, valid_to, traffic_cnt, air_traffic_load, relative_air_traffic_load)
values (%s, %s, null, %s, %s, %s)
on conflict (region_id, valid_from) do update
set traffic_cnt = excluded.traffic_cnt,
    air_traffic_load = excluded.air_traffic_load,
    relative_air_traffic_load = excluded.relative_air_traffic_load;
"""

SQL_UPSERT_FLIGHT = """
insert into flight(flight_number, center_id, uav_type_id, dep_timestamp, arr_timestamp, source_batch_id)
values (%s, %s, %s, %s, %s, %s)
on conflict (flight_number, dep_timestamp) do update
set center_id = excluded.center_id,
    uav_type_id = excluded.uav_type_id,
    arr_timestamp = excluded.arr_timestamp,
    source_batch_id = excluded.source_batch_id
returning id;
"""

SQL_INSERT_FLIGHT_LOC = """
insert into flight_loc(flight_id, takeoff_geom, landing_geom)
values (
  %s,
  ST_SetSRID(ST_MakePoint(%s, %s), 4326),
  ST_SetSRID(ST_MakePoint(%s, %s), 4326)
)
on conflict (flight_id) do update
set takeoff_geom = excluded.takeoff_geom,
    landing_geom = excluded.landing_geom;
"""

SQL_INSERT_FLIGHT_METRICS = """
insert into flight_metrics(flight_id, duration_min, distance, speed)
values (%s, %s, %s, %s)
on conflict (flight_id) do update
set duration_min = excluded.duration_min,
    distance     = excluded.distance,
    speed        = excluded.speed;
"""

SQL_INSERT_WEATHER_ONE = """
insert into weather_obs(flight_id, obs_timestamp, wind_dir, wind_speed, temperature_c, humidity_pct)
values (%s, %s, %s, %s, %s, %s)
on conflict (flight_id, obs_timestamp) do update
set wind_dir = excluded.wind_dir,
    wind_speed = excluded.wind_speed,
    temperature_c = excluded.temperature_c,
    humidity_pct  = excluded.humidity_pct;
"""

SQL_UPSERT_SEASON = """
insert into season_dim(code, display_name) values (%s, %s)
on conflict (code) do nothing;
"""

SQL_LINK_SEASON = """
insert into flight_season(flight_id, season_code) values (%s, %s)
on conflict (flight_id) do update set season_code = excluded.season_code;
"""

def load_all_data(filename):
    df = pd.read_excel(filename, sheet_name=0)

    # приведение заголовков
    cols = {src: dst for src, dst in COLUMN_MAP.items() if src in df.columns}
    df = df.rename(columns=cols)

    # timestamps
    df["dep_ts"] = [
        _none_if_nat(_combine_ts(r.get("dep_date"), r.get("dep_time")))
        for _, r in df.iterrows()
    ]
    df["arr_ts"] = [
        _none_if_nat(_combine_ts(r.get("arr_date"), r.get("arr_time")))
        for _, r in df.iterrows()
    ]

    # ВАЖНО: не делаем глобальный drop_duplicates — он терял строки с NaN flight_id
    # делаем дедуп только для тех, где flight_id заполнен
    if "flight_id" in df.columns:
        has_id = df[df["flight_id"].notna()]
        no_id = df[df["flight_id"].isna()]
        has_id = has_id.drop_duplicates(subset=["flight_id", "dep_ts"], keep="last")
        df = pd.concat([has_id, no_id], ignore_index=True)

    conn = _conn()
    conn.autocommit = False
    cur = conn.cursor()

    source_batch_id = dt.datetime.now().strftime("excel_%Y%m%d_%H%M%S")

    # счётчики
    total_rows = len(df)
    inserted = 0
    skipped_no_center_or_dep = 0
    row_errors = 0

    try:
        for idx, row in df.iterrows():
            try:
                center = (
                    str(row.get("center")).strip()
                    if not pd.isna(row.get("center"))
                    else None
                )
                uav_code = (
                    str(row.get("uav_type")).strip()
                    if not pd.isna(row.get("uav_type"))
                    else None
                )
                season = row.get("season")
                dep_ts = row.get("dep_ts")
                arr_ts = _none_if_nat(row.get("arr_ts"))

                # пропуск по обязательным атрибутам
                if not center or dep_ts is None:
                    # даже если пропускаем полёт — создадим код uav_type, чтобы не потерять справочник
                    if uav_code:
                        cur.execute(SQL_UPSERT_UAV, (uav_code,))
                        cur.fetchone()
                    skipped_no_center_or_dep += 1
                    continue

                # region
                cur.execute(SQL_UPSERT_REGION, (center,))
                region_id = cur.fetchone()[0]

                # region_stats
                valid_from = _first_day_of_month(dep_ts)
                traffic_cnt = row.get("traffic_cnt")
                air_load = row.get("air_traffic_load")
                rel_load = row.get("relative_air_traffic_load")
                if (
                    _is_number(traffic_cnt)
                    and _is_number(air_load)
                    and _is_number(rel_load)
                ):
                    cur.execute(
                        SQL_UPSERT_REGION_STATS,
                        (
                            region_id,
                            valid_from,
                            int(traffic_cnt),
                            float(air_load),
                            float(rel_load),
                        ),
                    )

                # uav_type (всегда прогоняем, даже если пустой — подменим на 'unknown')
                if not uav_code:
                    uav_code = "unknown"
                cur.execute(SQL_UPSERT_UAV, (uav_code,))
                uav_id = cur.fetchone()[0]

                # flight
                flight_num = _to_int_safe(row.get("flight_id"))
                cur.execute(
                    SQL_UPSERT_FLIGHT,
                    (flight_num, region_id, uav_id, dep_ts, arr_ts, source_batch_id),
                )
                flight_id = cur.fetchone()[0]

                # geometry (lon, lat)
                t_lon = row.get("takeoff_lon")
                t_lat = row.get("takeoff_lat")
                l_lon = row.get("landing_lon")
                l_lat = row.get("landing_lat")
                if (
                    _is_number(t_lon)
                    and _is_number(t_lat)
                    and _is_number(l_lon)
                    and _is_number(l_lat)
                ):
                    cur.execute(
                        SQL_INSERT_FLIGHT_LOC,
                        (
                            flight_id,
                            float(t_lon),
                            float(t_lat),
                            float(l_lon),
                            float(l_lat),
                        ),
                    )

                # metrics
                duration_min = row.get("duration_min")
                distance = row.get("distance")
                speed = row.get("speed")
                cur.execute(
                    SQL_INSERT_FLIGHT_METRICS,
                    (
                        flight_id,
                        float(duration_min) if _is_number(duration_min) else None,
                        float(distance) if _is_number(distance) else None,
                        float(speed) if _is_number(speed) else None,
                    ),
                )

                # weather
                wind_dir = row.get("wind_dir")
                wind_speed = row.get("wind_speed")
                temperature_c = row.get("temperature_c")
                humidity_pct = row.get("humidity_pct")
                if any(
                    _is_number(x)
                    for x in [wind_dir, wind_speed, temperature_c, humidity_pct]
                ):
                    cur.execute(
                        SQL_INSERT_WEATHER_ONE,
                        (
                            flight_id,
                            dep_ts,
                            float(wind_dir) if _is_number(wind_dir) else None,
                            float(wind_speed) if _is_number(wind_speed) else None,
                            float(temperature_c) if _is_number(temperature_c) else None,
                            float(humidity_pct) if _is_number(humidity_pct) else None,
                        ),
                    )

                # season
                if isinstance(season, str) and season.strip():
                    s = season.strip().lower()
                    cur.execute(SQL_UPSERT_SEASON, (s, s.capitalize()))
                    cur.execute(SQL_LINK_SEASON, (flight_id, s))

                inserted += 1

                if (idx + 1) % 1000 == 0:
                    conn.commit()

            except Exception as row_e:
                # не валим весь бэтч — считаем ошибку и идём дальше
                row_errors += 1
                # можно логировать конкретную строку при необходимости:
                # print(f"row {idx} error: {row_e}")
                continue

        conn.commit()
        print("ok: загрузка завершена")
        print(f"всего строк в excel: {total_rows}")
        print(f"загружено в flight: {inserted}")
        print(f"пропущено (нет center или dep_ts): {skipped_no_center_or_dep}")
        print(f"строк с ошибками при вставке (не закоммичено): {row_errors}")

    except Exception as e:
        conn.rollback()
        print("fail:", e)
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_all_data()