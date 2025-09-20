console.log("[DroneRadar] main.js загружен");

// Инициализируем карту
const map = L.map("map").setView([61.524, 105.3188], 3);

// Подложка OSM
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "", // убрали ссылку Leaflet
}).addTo(map);
// === ГОРОДА ===
const citySelect = document.getElementById("city-select");
let cityMarker = null;

fetch("/static/data/cities.geojson")
  .then(r => {
    if (!r.ok) throw new Error("cities.geojson not found");
    return r.json();
  })
  .then(geo => {
    console.log("[DroneRadar] cities:", geo.features?.length ?? 0);

    // Наполняем селект
    geo.features.forEach((f, idx) => {
      const name =
        f.properties?.name ||
        f.properties?.NAME ||
        `Город ${idx}`;

      if (f.geometry?.type !== "Point") return;
      const [lon, lat] = f.geometry.coordinates || [];
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;

      const opt = document.createElement("option");
      // кодируем координаты в value
      opt.value = `${lat},${lon}`;
      opt.textContent = name;
      citySelect.appendChild(opt);
    });

    citySelect.disabled = false;
  })
  .catch(err => {
    console.warn("Не удалось загрузить cities.geojson:", err);
    citySelect.title = "Файл cities.geojson не найден";
  });

// Центрирование и попап по выбору города
citySelect.addEventListener("change", (e) => {
  const val = e.target.value;
  if (!val) return;

  const [latStr, lonStr] = val.split(",");
  const lat = parseFloat(latStr);
  const lon = parseFloat(lonStr);
  const name = e.target.selectedOptions[0]?.textContent || "Город";

  if (Number.isFinite(lat) && Number.isFinite(lon)) {
    if (cityMarker) cityMarker.remove();
    cityMarker = L.marker([lat, lon]).addTo(map).bindPopup(name);
    map.setView([lat, lon], 7, { animate: true });

    // Откроем правый сайдбар как при клике по региону
    openSidebar(name, `<p>Город: ${name}</p>`);
  }
});

// Функция для каждого региона
function onEachFeature(feature, layer) {
  const regionName = feature.properties.name || feature.properties.name_latin || "Без названия";

  // тултип при наведении
  layer.bindTooltip(regionName);

  // подсветка при наведении
  layer.on("mouseover", function () {
    this.setStyle({ weight: 3, color: "yellow" });
  });
  layer.on("mouseout", function () {
    geoLayer.resetStyle(this); // сбрасываем стиль к базовому
  });

  // клик по региону
  layer.on("click", function () {
    map.fitBounds(layer.getBounds());
    openSidebar(regionName, `<p>Информация про ${regionName}</p>`);
  });

  // сохраним в справочник для селекта
  featuresMap[regionName] = layer;
}

let geoLayer; // слой с регионами
let featuresMap = {}; // сопоставление название → слой

fetch("/static/data/russia.geojson")
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

    // Заполняем селект
    const select = document.getElementById("region-select");
    geojson.features.forEach((f, idx) => {
      const name = f.properties.name || f.properties.name_latin || `Регион ${idx}`;
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      select.appendChild(option);
    });

    // Обработчик выбора из списка
    select.addEventListener("change", (e) => {
      const name = e.target.value;
      if (!name) return;

      const layer = featuresMap[name];
      if (layer) {
        map.fitBounds(layer.getBounds());     // центрируем карту
        layer.fire("click");                  // эмулируем клик → откроет сайдбар
      }
    });
  })
  .catch((err) => console.error("Ошибка загрузки GeoJSON:", err));

map.attributionControl.setPrefix(false);
