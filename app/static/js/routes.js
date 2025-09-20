console.log("[DroneRadar] routes.js загружен");

// featureGroup вместо layerGroup → есть getBounds()
let routeLayer = L.featureGroup().addTo(map);

function drawRoutes(routes) {
  // очищаем слой
  routeLayer.clearLayers();

  routes.forEach((route, idx) => {
    const lineCoords = route.points.map(p => p.coords);

    // polyline без маркеров
    L.polyline(lineCoords, {
      color: ["red", "blue", "green", "purple"][idx % 4],
      weight: 1,          // толщина линии (в пикселях)
      opacity: 1.0,       // непрозрачность
      lineCap: "round",   // сглаженные концы
      lineJoin: "round",  // сглаженные стыки
    }).addTo(routeLayer);
  });

  if (routes.length > 0) {
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] });
  }
}

async function fetchRoutes() {
  try {
    const res = await fetch("/static/data/routes.json?_=" + Date.now()); 
    const routes = await res.json();
    console.log("[DroneRadar] маршрутов загружено:", routes.length);
    drawRoutes(routes);
  } catch (err) {
    console.error("[DroneRadar] ошибка загрузки маршрутов:", err);
  }
}

// первая загрузка
fetchRoutes();

// автообновление каждые 10 секунд
setInterval(fetchRoutes, 10000);
