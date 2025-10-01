// components/DroneRadarEmbeddable.jsx
import React, { useState } from 'react';
import DroneMap from './DroneMap';
import MapControls from './MapControls';
import MapSidebar from './MapSidebar';
import InfoPanels from './InfoPanels';
import './DroneRadarEmbeddable.css';

const DroneRadarEmbeddable = ({
  // Пропсы для контейнера
  containerId = "drone-radar-embedded",
  className = "",
  
  // Пропсы для данных
  initialCities = [],
  initialRegions = [],
  
  // Колбэки
  onMapReady,
  onCitySelect,
  onRegionSelect,
  onFilter,
  onModeToggle,
  
  // Состояние UI
  initialSidebarOpen = false,
  initialPanels = []
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(initialSidebarOpen);
  const [sidebarContent, setSidebarContent] = useState("");
  const [sidebarTitle, setSidebarTitle] = useState("Регион");
  const [panels, setPanels] = useState(initialPanels);
  const [mapInstance, setMapInstance] = useState(null);

  const handleMapReady = (map) => {
    setMapInstance(map);
    if (onMapReady) onMapReady(map);
    
    // Здесь можно добавить маркеры, слои и т.д.
    setupMapFeatures(map);
  };

  const setupMapFeatures = (map) => {
    // Пример: добавляем обработчик клика по карте
    map.on('click', (e) => {
      setSidebarTitle("Выбранная точка");
      setSidebarContent(`Координаты: ${e.latlng.lat.toFixed(4)}, ${e.latlng.lng.toFixed(4)}`);
      setSidebarOpen(true);
    });
  };

  const handleRegionSelect = (regionId) => {
    if (onRegionSelect) onRegionSelect(regionId);
    // Обновляем сайдбар при выборе региона
    if (regionId) {
      setSidebarTitle("Информация о регионе");
      setSidebarContent(`Загружаем данные для региона ${regionId}...`);
      setSidebarOpen(true);
    }
  };

  const handlePanelClose = (panelId) => {
    setPanels(panels.map(panel => 
      panel.id === panelId ? { ...panel, isOpen: false } : panel
    ));
  };

  const defaultPanels = [
    {
      id: 'chart-1',
      title: 'Диаграмма 1',
      content: 'Здесь будет график или таблица',
      position: 'left-top',
      isOpen: true
    },
    {
      id: 'chart-2', 
      title: 'Диаграмма 2',
      content: 'Здесь будет гистограмма или текст',
      position: 'left-bottom',
      isOpen: true
    }
  ];

  return (
    <div id={containerId} className={`drone-radar-embedded ${className}`}>
      {/* Карта */}
      <DroneMap
        containerId={`${containerId}-map`}
        onMapReady={handleMapReady}
        onRegionSelect={handleRegionSelect}
        onCitySelect={onCitySelect}
      />
      
      {/* Элементы управления */}
      <MapControls
        cities={initialCities}
        regions={initialRegions}
        onCityChange={onCitySelect}
        onRegionChange={handleRegionSelect}
        onFilterClick={onFilter}
        onModeToggle={onModeToggle}
        className="embedded-controls"
      />
      
      {/* Сайдбар */}
      <MapSidebar
        isOpen={sidebarOpen}
        title={sidebarTitle}
        onClose={() => setSidebarOpen(false)}
        position="right"
      >
        {sidebarContent}
      </MapSidebar>
      
      {/* Информационные панели */}
      <InfoPanels
        panels={panels.length > 0 ? panels : defaultPanels}
        onPanelClose={handlePanelClose}
      />
    </div>
  );
};

export default DroneRadarEmbeddable;