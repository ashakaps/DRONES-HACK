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

