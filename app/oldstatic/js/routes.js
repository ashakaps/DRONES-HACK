function openSidebar(regionName, infoHtml) {
  // Заполняем правый сайдбар
  const title = document.getElementById("sidebar-title");
  const content = document.getElementById("sidebar-content");
  if (title) title.innerText = regionName;
  if (content) content.innerHTML = infoHtml;

  // Открываем все три панели, если они есть
  ["sidebar", "sidebar-left-top", "sidebar-left-bottom"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add("visible");
  });
}

function closeAllSidebars() {
  ["sidebar", "sidebar-left-top", "sidebar-left-bottom"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.remove("visible");
  });
}

// Закрыть все сайдбары (правая панель)
document.querySelector("#sidebar .sidebar-close")
  .addEventListener("click", closeAllSidebars);

// Закрыть только свой сайдбар (для левых панелей)
["sidebar-left-top", "sidebar-left-bottom"].forEach(id => {
  const el = document.querySelector(`#${id} .sidebar-close`);
  if (el) {
    el.addEventListener("click", () => {
      document.getElementById(id).classList.remove("visible");
    });
  }
});

console.log("[DroneRadar] routes.js загружен");

let routeLayer = L.featureGroup().addTo(map);
let firstRoutesLoad = true; // флаг для первого зума

function drawRoutes(routes) {
  // очистка
  routeLayer.clearLayers();

  if (!Array.isArray(routes)) {
    console.warn("[routes] ожидался массив, пришло:", routes);
    return;
  }

  routes.forEach((route, idx) => {
    const lineCoords = (route.points || []).map(p => p.coords);

    const polyline = L.polyline(lineCoords, {
      color: ["#ef4444", "#3b82f6", "#10b981", "#a855f7"][idx % 4],
      weight: 1,           // толщина линии (px, не зависит от зума)
      opacity: 0.1,
      lineCap: "round",
      lineJoin: "round",
    }).addTo(routeLayer);

    // положим данные маршрута в слой
    polyline.routeData = route;

    // клик по линии — показываем инфо в правом сайдбаре
    polyline.on("click", () => {
      const title = route?.meta?.name || route.id || "Маршрут";
      const html = `
        <div>
          <div><b>ID:</b> ${route.id ?? "-"}</div>
          <div><b>DB ID:</b> ${route.db_id ?? "-"}</div>
          <div><b>Точек:</b> ${route.points?.length ?? 0}</div>
          ${route?.meta?.status ? `<div><b>Статус:</b> ${route.meta.status}</div>` : ""}
          ${route?.meta?.length_km ? `<div><b>Длина:</b> ${route.meta.length_km} км</div>` : ""}
        </div>`;
      openSidebar(title, html);
    });
  });

  // Зум только при первой загрузке
  if (routeLayer.getLayers().length && firstRoutesLoad) {
    map.fitBounds(routeLayer.getBounds(), { padding: [40, 40] });
    firstRoutesLoad = false;
  }
}

async function fetchRoutes() {
  try {
    const res = await fetch("/static/data/routes.json?_=" + Date.now());
    const data = await res.json();
    console.log("[DroneRadar] маршрутов загружено:", Array.isArray(data) ? data.length : "не массив");
    drawRoutes(data);
  } catch (e) {
    console.error("[DroneRadar] ошибка загрузки маршрутов:", e);
  }
}

// первая загрузка + автообновление
fetchRoutes();
setInterval(fetchRoutes, 10000);
