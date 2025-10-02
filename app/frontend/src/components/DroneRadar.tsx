
// DroneRadar.tsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import type { GeoJSON as GeoJSONType, Feature, FeatureCollection } from "geojson";
import L, { GeoJSON as LGeoJSON, Layer } from "leaflet";
import "leaflet/dist/leaflet.css";

// Небольшие утилиты
type IdName = { id: string | number; name: string };

async function fetchJSON<T>(url: string): Promise<T> {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return r.json();
}

// Тип для GeoJSON городов
type CityFC = FeatureCollection<
  GeoJSON.Point,
  { id: number | string; name: string }
>;
type RegionFC = FeatureCollection<
  GeoJSON.MultiPolygon | GeoJSON.Polygon | GeoJSON.Point | GeoJSON.MultiPoint,
  { id: number | string; name: string }
>;

async function fetchCities(): Promise<IdName[]> {
  const fc = await fetchJSON<CityFC>("/geo/cities");
  return (fc.features || [])
    .map(f => f.properties)
    .filter((p): p is { id: number | string; name: string } => !!p && p.id != null && !!p.name)
    .map(p => ({ id: p.id, name: p.name }));
}

async function fetchRegions(): Promise<IdName[]> {
  const fc = await fetchJSON<RegionFC>("/geo/regions");
  return (fc.features || [])
    .map(f => f.properties)
    .filter((p): p is { id: number | string; name: string } => !!p && p.id != null && !!p.name)
    .map(p => ({ id: p.id, name: p.name }));
}


/*
const fetchFeatures = (city?: string, region?: string) => {
  const qs = new URLSearchParams();
  if (city) qs.set("city", city);
  if (region) qs.set("region", region);
  const url = `/geo/features${qs.toString() ? `?${qs}` : ""}`;
  return fetchJSON<FeatureCollection>(url);
};
*/

/*
const fetchCharts = (city?: string, region?: string) => {
  const qs = new URLSearchParams();
  if (city) qs.set("city", city);
  if (region) qs.set("region", region);
  return fetchJSON<{ weekly_by_city: string; hourly_dayparts: string }>(
    `/charts${qs.toString() ? `?${qs}` : ""}`,
  );
};
*/

type Mode = "default" | "alt";

export default function DroneRadar() {
  // Списки и выбранные фильтры (топбар)
  const [cities, setCities] = useState<IdName[]>([]);
  const [regions, setRegions] = useState<IdName[]>([]);
  const [city, setCity] = useState<string>("");
  const [region, setRegion] = useState<string>("");

  // Данные карты и режим отображения
  const [features, setFeatures] = useState<FeatureCollection | null>(null);
  const [mode, setMode] = useState<Mode>("default");

  // Сайдбары/чарты
  const [rightOpen, setRightOpen] = useState(false);
  const [rightTitle, setRightTitle] = useState<string>("Регион");
  const [charts, setCharts] = useState<{ weekly_by_city?: string; hourly_dayparts?: string }>({});

  // Первичная загрузка справочников
  useEffect(() => {
    fetchCities().then((cities) => {
        setCities(cities);
        console.log("Loaded cities:", cities);
    }).catch(console.error);
    fetchRegions().then(setRegions).catch(console.error);
  }, []);

  // Загрузка фич и картинок
  const loadData = React.useCallback(async () => {
    try {
        /*
      const [ fc, ch] = await Promise.all([
          fetchFeatures(city || undefined, region || undefined),
          fetchCharts(city || undefined, region || undefined)
      ]);
      setFeatures(fc);
      setCharts(ch);
      */
     console.log("LoadData: TODO");
    } catch (e) {
      console.error(e);
    }
  }, [city, region]);

  // Автозагрузка при изменении фильтров
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Стили геометрий
  const style = useMemo<L.PathOptions>(() => {
    return mode === "default"
      ? { color: "#1976d2", weight: 2, fillOpacity: 0.15 }
      : { color: "#9c27b0", weight: 2, dashArray: "4 3", fillOpacity: 0.1 };
  }, [mode]);

  // Хэндлеры фич
  const onEachFeature = (_feature: Feature, layer: Layer) => {
    layer.on("click", () => {
      const name =
        (typeof _feature.properties?.name === "string" && _feature.properties.name) ||
        (typeof _feature.properties?.title === "string" && _feature.properties.title) ||
        "Регион";
      setRightTitle(name);
      setRightOpen(true);
    });
    // Тултип по наведению
    if (_feature.properties && (_feature.properties as any).name) {
      layer.bindTooltip(String((_feature.properties as any).name), { sticky: true });
    }
  };

  // fitBounds по данным
  const geoRef = useRef<LGeoJSON>(null);
  useEffect(() => {
    const g = geoRef.current;
    if (g && features && (g as any)?._map) {
      try {
        const bounds = g.getBounds();
        if (bounds.isValid()) (g as any)._map.fitBounds(bounds, { padding: [20, 20] });
      } catch {}
    }
  }, [features]);

  return (
    <div className="drone-radar-root" style={{ height: "100%", width: "100%", display: "flex", flexDirection: "column" }}>
      {/* TOPBAR (как в index.html: заголовок, два select и две кнопки) */}
      <div
        style={{
          height: 56,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 12px",
          borderBottom: "1px solid var(--border,#2a2a2a)",
          background: "var(--bg,#111)",
          color: "var(--fg,#eee)",
          gap: 12,
        }}
      >
        <span style={{ fontWeight: 600 }}>DroneRadar</span>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <select
            aria-label="Выберите город"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            style={{ height: 36, background: "transparent", color: "inherit", border: "1px solid #444", borderRadius: 8, padding: "0 8px" }}
          >
            <option value="">Выберите город…</option>
            {cities.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.name}
              </option>
            ))}
          </select>

          <select
            aria-label="Выберите регион"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            style={{ height: 36, background: "transparent", color: "inherit", border: "1px solid #444", borderRadius: 8, padding: "0 8px" }}
          >
            <option value="">Выберите регион…</option>
            {regions.map((r) => (
              <option key={r.id} value={String(r.id)}>
                {r.name}
              </option>
            ))}
          </select>

          <button
            onClick={loadData}
            style={{ height: 36, padding: "0 12px", borderRadius: 8, border: "1px solid #444", background: "#1f2937", color: "#e5e7eb" }}
          >
            Фильтр
          </button>
          <button
            onClick={() => setMode((m) => (m === "default" ? "alt" : "default"))}
            style={{ height: 36, padding: "0 12px", borderRadius: 8, border: "1px solid #444", background: "#374151", color: "#e5e7eb" }}
          >
            Режим
          </button>
        </div>
      </div>

      {/* Контент: карта + правый сайдбар + два левых бокса-виджета */}
      <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
        <MapContainer
          style={{ position: "absolute", inset: 0 }}
          center={[34.707, 33.022]}
          zoom={8}
          scrollWheelZoom
        >
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {features && (
            <GeoJSON
              ref={geoRef as any}
              data={features as unknown as GeoJSONType}
              style={() => style}
              onEachFeature={onEachFeature}
            />
          )}
        </MapContainer>

        {/* Правый сайдбар (как в index.html) */}
        <aside
          aria-label="Правый сайдбар"
          style={{
            position: "absolute",
            top: 0,
            right: 0,
            height: "100%",
            width: rightOpen ? 360 : 0,
            transition: "width 160ms ease",
            overflow: "hidden",
            background: "rgba(17,17,17,0.96)",
            borderLeft: "1px solid #2a2a2a",
            color: "#e5e7eb",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 12, borderBottom: "1px solid #2a2a2a" }}>
            <span style={{ fontWeight: 600 }}>{rightTitle}</span>
            <button
              onClick={() => setRightOpen(false)}
              aria-label="Закрыть"
              style={{ width: 32, height: 32, borderRadius: 6, border: "1px solid #444", background: "#222", color: "#eee" }}
            >
              ×
            </button>
          </div>
          <div style={{ padding: 12, display: "grid", gap: 12 }}>
            <div style={{ minHeight: 120, border: "1px dashed #444", borderRadius: 10 }} />
            <div style={{ minHeight: 120, border: "1px dashed #444", borderRadius: 10 }} />
            <div style={{ minHeight: 120, border: "1px dashed #444", borderRadius: 10 }} />
          </div>
        </aside>

        {/* Левый верхний бокс (Диаграмма 1) */}
        <div
          style={{
            position: "absolute",
            top: 12,
            left: 12,
            width: 320,
            background: "rgba(17,17,17,0.96)",
            border: "1px solid #2a2a2a",
            borderRadius: 14,
            overflow: "hidden",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 10, borderBottom: "1px solid #2a2a2a", color: "#e5e7eb" }}>
            <span style={{ fontWeight: 600 }}>Диаграмма 1</span>
            {/* Для симметрии оставим икс, как в исходнике */}
            <button aria-label="Закрыть" style={{ width: 28, height: 28, borderRadius: 6, border: "1px solid #444", background: "#222", color: "#eee" }}>
              ×
            </button>
          </div>
          <div style={{ padding: 10 }}>
            {/* Аналог <img id="chart-weekly_by_city" .../> */}
            {charts.weekly_by_city ? (
              <img src={charts.weekly_by_city} alt="График weekly_by_city" style={{ width: "100%", display: "block", borderRadius: 8 }} />
            ) : (
              <div style={{ height: 160, border: "1px dashed #444", borderRadius: 10 }} />
            )}
          </div>
        </div>

        {/* Левый нижний бокс (Диаграмма 2) */}
        <div
          style={{
            position: "absolute",
            left: 12,
            bottom: 12,
            width: 320,
            background: "rgba(17,17,17,0.96)",
            border: "1px solid #2a2a2a",
            borderRadius: 14,
            overflow: "hidden",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: 10, borderBottom: "1px solid #2a2a2a", color: "#e5e7eb" }}>
            <span style={{ fontWeight: 600 }}>Диаграмма 2</span>
            <button aria-label="Закрыть" style={{ width: 28, height: 28, borderRadius: 6, border: "1px solid #444", background: "#222", color: "#eee" }}>
              ×
            </button>
          </div>
          <div style={{ padding: 10 }}>
            {/* Аналог <img id="chart-hourly_dayparts" .../> */}
            {charts.hourly_dayparts ? (
              <img src={charts.hourly_dayparts} alt="График hourly_dayparts" style={{ width: "100%", display: "block", borderRadius: 8 }} />
            ) : (
              <div style={{ height: 160, border: "1px dashed #444", borderRadius: 10 }} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
