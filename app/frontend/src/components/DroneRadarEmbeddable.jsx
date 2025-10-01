// components/DroneRadarEmbeddable.jsx
import React, { useState } from 'react';
import DroneMap from './DroneMap';
import MapControls from './MapControls';
import MapSidebar from './MapSidebar';
import InfoPanels from './InfoPanels';
import './DroneRadarEmbeddable.css';

const DroneRadarEmbeddable = ({
  containerId = "drone-radar-embedded",
  className = "",
  initialCities = [],
  initialRegions = [],
  onMapReady,
  onCitySelect,
  onRegionSelect,
  onFilter,
  onModeToggle
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarContent, setSidebarContent] = useState("");
  const [sidebarTitle, setSidebarTitle] = useState("Регион");

  const handleMapReady = (map) => {
    console.log('DroneRadarEmbeddable - Map ready');
    if (onMapReady) onMapReady(map);
    
    // Настройка обработчиков карты
    map.on('click', (e) => {
      setSidebarTitle("Выбранная точка");
      setSidebarContent(`
        <h4>Координаты:</h4>
        <p>Широта: ${e.latlng.lat.toFixed(6)}</p>
        <p>Долгота: ${e.latlng.lng.toFixed(6)}</p>
      `);
      setSidebarOpen(true);
    });
  };

  const handleRegionSelect = (regionId) => {
    console.log('DroneRadarEmbeddable - Region selected:', regionId);
    if (onRegionSelect) onRegionSelect(regionId);
    
    if (regionId) {
      const region = initialRegions.find(r => r.id === regionId);
      setSidebarTitle(region ? region.name : "Информация о регионе");
      setSidebarContent(`
        <h4>Данные региона:</h4>
        <p>Загружаем статистику для региона ${regionId}...</p>
        <ul>
          <li>Количество дронов: 15</li>
          <li>Активных миссий: 3</li>
          <li>Покрытие территории: 75%</li>
        </ul>
      `);
      setSidebarOpen(true);
    }
  };

  const handleCitySelect = (cityId) => {
    console.log('DroneRadarEmbeddable - City selected:', cityId);
    if (onCitySelect) onCitySelect(cityId);
  };

  return (
    <div id={containerId} className={`drone-radar-embedded ${className}`}>
      <DroneMap
        containerId={`${containerId}-map`}
        onMapReady={handleMapReady}
      />
      
      <MapControls
        cities={initialCities}
        regions={initialRegions}
        onCityChange={handleCitySelect}
        onRegionChange={handleRegionSelect}
        onFilterClick={onFilter}
        onModeToggle={onModeToggle}
        className="embedded-controls"
      />
      
      <MapSidebar
        isOpen={sidebarOpen}
        title={sidebarTitle}
        onClose={() => setSidebarOpen(false)}
        position="right"
      >
        <div dangerouslySetInnerHTML={{ __html: sidebarContent }} />
      </MapSidebar>
      
      <InfoPanels />
    </div>
  );
};

export default DroneRadarEmbeddable;