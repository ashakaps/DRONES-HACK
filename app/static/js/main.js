console.log("[DroneRadar] main.js загружен");

// === КАРТА ===
const map = L.map("map").setView([61.524, 105.3188], 3);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "",
}).addTo(map);
map.attributionControl.setPrefix(false);

let geoLayer; // слой регионов
let featuresMap = {}; // справочник регион → слой
let cityMarker = null;

// === УТИЛИТЫ ДЛЯ САЙДБАРОВ И ГРАФИКОВ ===

// загрузка одного графика в контейнер
async function loadChart(containerId, chartName, city = null) {
  try {
    let url = `/charts/${chartName}`;
    if (city) url += `?city=${encodeURIComponent(city)}`;

    const res = await fetch(url);
    const data = await res.json();

    const el = document.getElementById(containerId);
    if (!el) return;

    el.innerHTML = "";
    if (data.path) {
      const img = document.createElement("img");
      img.src = data.path + "?t=" + Date.now(); // анти-кэш
      el.appendChild(img);
    } else {
      el.innerHTML = `<p style="color:#c00;">${data.error || "Ошибка загрузки"}</p>`;
    }
  } catch (e) {
    console.error("[Charts] loadChart error:", e);
    const el = document.getElementById(containerId);
    if (el) el.innerHTML = `<p style="color:#c00;">Ошибка сети</p>`;
  }
}

// открыть панели и заголовок
function loadChartsForCity(cityName) {
  openPanelsForCity(cityName);

  // Пока грузим только один график (правый сайдбар)
  loadChart("chart-right-1", "monthly_total");

  // Остальные добавим позже
  // loadChart("chart-left-top", "weekly_by_city", cityName);
  // loadChart("chart-left-bottom", "hourly_dayparts");
  // loadChart("chart-right-3", "city_monthly_trend", cityName);
}


// === ГОРОДА ===
const citySelect = document.getElementById("city-select");
fetch("/geo/cities")
  .then((r) => {
    if (!r.ok) throw new Error("cities.geojson not found");
    return r.json();
  })
  .then((geo) => {
    console.log("[DroneRadar] cities:", geo.features?.length ?? 0);

    geo.features.forEach((f, idx) => {
      if (f.geometry?.type !== "Point") return;
      const [lon, lat] = f.geometry.coordinates || [];
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const name =
        f.properties?.name ||
        f.properties?.NAME ||
        f.properties?.center ||
        f.properties?.name ||
        `Город ${idx}`;

      // добавим в селект
      const opt = document.createElement("option");
      opt.value = `${lat},${lon},${name}`;
      opt.textContent = name;
      citySelect.appendChild(opt);
    });

    citySelect.disabled = false;
  })
  .catch((err) => {
    console.warn("Не удалось загрузить cities.geojson:", err);
    citySelect.title = "Файл cities.geojson не найден";
  });

// обработчик выбора города из селекта
citySelect.addEventListener("change", (e) => {
  const val = e.target.value;
  if (!val) return;

  const [latStr, lonStr, cityName] = val.split(",");
  const lat = parseFloat(latStr);
  const lon = parseFloat(lonStr);

  if (Number.isFinite(lat) && Number.isFinite(lon)) {
    if (cityMarker) cityMarker.remove();
    cityMarker = L.marker([lat, lon]).addTo(map).bindPopup(cityName);
    map.setView([lat, lon], 7, { animate: true });

    loadChartsForCity(cityName);
  }
});

// === РЕГИОНЫ ===

// callback для каждого региона
function onEachFeature(feature, layer) {
  const regionName =
    feature.properties.name ||
    feature.properties.name_latin ||
    "Без названия";

  layer.bindTooltip(regionName);

  layer.on("mouseover", function () {
    this.setStyle({ weight: 3, color: "yellow" });
  });
  layer.on("mouseout", function () {
    geoLayer.resetStyle(this);
  });

  layer.on("click", function () {
    map.fitBounds(layer.getBounds());
    openPanelsForCity(regionName);

    // здесь можно тоже подгружать общие графики для региона,
    // если планируется (сейчас графики завязаны на города)
  });

  featuresMap[regionName] = layer;
}

fetch("/geo/regions")
  .then((resp) => resp.json())
  .then((geojson) => {
    console.log("[DroneRadar] features:", geojson.features.length);

    geoLayer = L.geoJSON(geojson, {
      style: {
        color: "blue",
        weight: 1,
        fillColor: "lightblue",
        fillOpacity: 0.5,
      },
      onEachFeature: onEachFeature,
    }).addTo(map);

    // заполняем селект регионов
    const select = document.getElementById("region-select");
    geojson.features.forEach((f, idx) => {
      const name =
        f.properties.name ||
        f.properties.name_latin ||
        `Регион ${idx}`;
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.appendChild(option);
    });

    select.addEventListener("change", (e) => {
      const name = e.target.value;
      if (!name) return;
      const layer = featuresMap[name];
      if (layer) {
        map.fitBounds(layer.getBounds());
        layer.fire("click");
      }
    });
  })
  .catch((err) => console.error("Ошибка загрузки GeoJSON:", err));
console.log(geojson.features[0].properties);
