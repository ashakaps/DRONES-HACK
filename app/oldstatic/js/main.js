console.log("[DroneRadar] main.js загружен");

// === КАРТА ===
const map = L.map("map").setView([61.524, 105.3188], 3);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "",
}).addTo(map);
map.attributionControl.setPrefix(false);

// === ГЛОБАЛЬНЫЕ СОСТОЯНИЯ ===
let geoLayer = null;          // интерактивный слой регионов (из БД)
let featuresMap = {};         // имя региона -> Leaflet layer
let cityMarker = null;        // маркер выбранного города

// === УТИЛИТЫ ДЛЯ САЙДБАРОВ И ГРАФИКОВ ===
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

// гарантируем наличие функции (если её нет в sidebar.js)
function openPanelsForCity(name) {
  try {
    const title = document.getElementById("sidebar-title");
    if (title) title.innerText = name || "Регион";

    ["sidebar", "sidebar-left-top", "sidebar-left-bottom"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.classList.add("visible");
      // если в index.html у панели есть класс hidden — снимем его
      if (el && el.classList.contains("hidden")) el.classList.remove("hidden");
    });
  } catch (e) {
    console.debug("[UI] openPanelsForCity fallback:", e);
  }
}

function loadChartsForCity(cityName) {
  openPanelsForCity(cityName);
  // Пока грузим только один график (правый сайдбар)
  // верхний левый сайдбар
  loadChart("chart-left-top", "top10_regions");

  // нижний левый сайдбар
  loadChart("chart-left-bottom", "monthly_total");

  // правый сайдбар
  loadChart("chart-right-3", "weekly_by_city", cityName);

  // Остальные вернёшь позже
  // loadChart("chart-left-top", "weekly_by_city", cityName);
  // loadChart("chart-left-bottom", "hourly_dayparts");
  // loadChart("chart-right-3", "city_monthly_trend", cityName);
}

// === ПОМОЩНИКИ ДЛЯ СЕЛЕКТОВ ===
function clearSelectKeepPlaceholder(selectEl) {
  if (!selectEl) return;
  const first = selectEl.firstElementChild?.cloneNode(true);
  selectEl.innerHTML = "";
  if (first) selectEl.appendChild(first); // оставляем placeholder
}

function addOption(selectEl, value, label) {
  const opt = document.createElement("option");
  opt.value = value;
  opt.textContent = label;
  selectEl.appendChild(opt);
}

// === ГОРОДА ===
const citySelect = document.getElementById("city-select");

fetch("/geo/cities")
  .then((r) => {
    if (!r.ok) throw new Error("GET /geo/cities failed");
    return r.json();
  })
  .then((geo) => {
    console.log("[DroneRadar] cities features:", geo.features?.length ?? 0);
    clearSelectKeepPlaceholder(citySelect);

    (geo.features ?? []).forEach((f, idx) => {
      if (f.geometry?.type !== "Point") return;
      const [lon, lat] = f.geometry.coordinates || [];
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const name = f.properties?.name ?? `Город ${idx}`;
      addOption(citySelect, `${lat},${lon},${name}`, name);
    });

    citySelect.disabled = false;
  })
  .catch((err) => {
    console.warn("[DroneRadar] Не удалось загрузить /geo/cities:", err);
    if (citySelect) citySelect.title = "Не удалось загрузить список городов";
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
function onEachFeature(feature, layer) {
  const regionName =
    feature?.properties?.name ||
    feature?.properties?.name_latin ||
    "Без названия";

  layer.bindTooltip(regionName);

  layer.on("mouseover", function () {
    this.setStyle({ weight: 3, color: "yellow" });
  });

  layer.on("mouseout", function () {
    if (geoLayer) geoLayer.resetStyle(this);
  });

  layer.on("click", function () {
    map.fitBounds(layer.getBounds());
    openPanelsForCity(regionName);
    // тут можно подгружать графики для региона, если будет нужно
  });

  featuresMap[regionName] = layer;
}

// 1) Декоративный слой со всеми регионами России (только фронт, не в списках)
fetch("/static/data/russia_full.geojson")
  .then((resp) => resp.json())
  .then((geojson) => {
    console.log("[DroneRadar] russia_full loaded:", geojson.features?.length ?? 0);
    L.geoJSON(geojson, {
      style: {
        color: "gray",
        weight: 1,
        fillColor: "lightgray",
        fillOpacity: 0.2,
      },
      interactive: false, // отключаем клики и тултипы
    }).addTo(map);
  })
  .catch((err) => console.error("[DroneRadar] Ошибка загрузки russia_full.geojson:", err));

// 2) «Боевые» регионы из БД (кликабельные + в селекте)
fetch("/geo/regions")
  .then((resp) => resp.json())
  .then((geojson) => {
    const count = geojson?.features?.length ?? 0;
    console.log("[DroneRadar] regions from DB:", count);
    if (!count) {
      console.warn("[DroneRadar] /geo/regions пуст или невалиден");
      return;
    }

    // рисуем интерактивный слой
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
    clearSelectKeepPlaceholder(select);

    geojson.features.forEach((f, idx) => {
      const name =
        f?.properties?.name ||
        f?.properties?.name_latin ||
        `Регион ${idx}`;
      addOption(select, name, name);
    });

    // обработчик выбора региона
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
  .catch((err) => console.error("[DroneRadar] Ошибка загрузки /geo/regions:", err));
document.getElementById("btn-mode").addEventListener("click", () => {
  const citySelect = document.getElementById("city-select");
  const city = citySelect.value || "Москва";

  fetch(`/charts/report_json?city=${encodeURIComponent(city)}`)
    .then(resp => resp.json())
    .then(data => {
      console.log("JSON отчёт:", data);

      // скачивание в виде файла
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${city}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    })
    .catch(err => console.error("Ошибка загрузки отчёта:", err));
});
