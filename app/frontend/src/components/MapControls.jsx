// components/MapControls.jsx
import React, { useEffect, useState } from 'react';
import './MapControls.css';

const MapControls = ({
  cities = null,
  regions = [],
  onCityChange,
  onRegionChange,
  onFilterClick,
  onModeToggle,
  className = ""
}) => {
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');

    console.log("Cities in mapControls: ", cities);

    const cityNames1 = [];
    if (cities) {
        cities.features.forEach(feature => {
            if (feature.properties && feature.properties.name) {
                cityNames1.push(feature.properties.name);
            }
        });
        console.log(cityNames1);
    }
  useEffect(() => {
    // Динамически загружаем Choices.js
    loadChoices();
  }, []);

  const loadChoices = () => {
    if (document.querySelector('#choices-script')) return;

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/choices.js/public/assets/styles/choices.min.css';
    document.head.appendChild(link);

    const script = document.createElement('script');
    script.id = 'choices-script';
    script.src = 'https://cdn.jsdelivr.net/npm/choices.js/public/assets/scripts/choices.min.js';
    document.head.appendChild(script);
  };

  const handleCityChange = (e) => {
    const value = e.target.value;
    setSelectedCity(value);
    if (onCityChange) onCityChange(value);
  };

  const handleRegionChange = (e) => {
    const value = e.target.value;
    setSelectedRegion(value);
    if (onRegionChange) onRegionChange(value);
  };

  return (
    <div className={`map-controls ${className}`}>
      <div className="controls-group">
        <select 
          value={selectedCity}
          onChange={handleCityChange}
          className="control-select"
        >
          <option value="">Выберите город...</option>
          {cityNames1.map(city => (
            <option key={city.id} value={city.id}>
              {city.name}
            </option>
          ))}
        </select>

        <select 
          value={selectedRegion}
          onChange={handleRegionChange}
          className="control-select"
        >
          <option value="">Выберите регион...</option>
          {regions.map(region => (
            <option key={region.id} value={region.id}>
              {region.name}
            </option>
          ))}
        </select>

        <button 
          onClick={onFilterClick}
          className="control-btn"
        >
          Фильтр
        </button>

        <button 
          onClick={onModeToggle}
          className="control-btn"
        >
          Режим
        </button>
      </div>
    </div>
  );
};

export default MapControls;
