// src/pages/OperatorDashboard.jsx  
import React from 'react';
import { useAuth } from '../context/AuthContext';
import DroneRadarEmbeddable from '../components/DroneRadarEmbeddable';
import './OperatorDashboard.css';

const OperatorDashboard = () => {
  const { user, logout } = useAuth();

  // Данные для карты
  const cities = [
    { id: 'moscow', name: 'Москва' },
    { id: 'spb', name: 'Санкт-Петербург' },
    { id: 'kazan', name: 'Казань' }
  ];

  const regions = [
    { id: 'central', name: 'Центральный федеральный округ' },
    { id: 'northwest', name: 'Северо-Западный федеральный округ' },
    { id: 'volga', name: 'Приволжский федеральный округ' }
  ];

  const handleMapReady = (map) => {
    console.log('Карта готова для оператора:', map);
  };

  const handleCitySelect = (cityId) => {
    console.log('Оператор выбрал город:', cityId);
  };

  const handleRegionSelect = (regionId) => {
    console.log('Оператор выбрал регион:', regionId);
  };

  return (
    <div className="operator-dashboard">
      <header className="dashboard-header">
        <h1>Панель оператора</h1>
        <div className="user-info">
          <span>{user?.email}</span>
          <button onClick={logout} className="logout-btn">Выйти</button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="actions-panel">
          <button className="btn-secondary" onClick={() => window.location.href = '/profile'}>
            Мой профиль
          </button>
        </div>

        <div className="map-container">
          <DroneRadarEmbeddable
            containerId="operator-map"
            className="operator-map"
            initialCities={cities}
            initialRegions={regions}
            onMapReady={handleMapReady}
            onCitySelect={handleCitySelect}
            onRegionSelect={handleRegionSelect}
            onFilter={() => console.log('Фильтр применен')}
            onModeToggle={() => console.log('Режим переключен')}
          />
        </div>
      </div>
    </div>
  );
};

export default OperatorDashboard;