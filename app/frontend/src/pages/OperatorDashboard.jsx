// src/pages/OperatorDashboard.js
import React from 'react';
import { useAuth } from '../context/AuthContext';
import './OperatorDashboard.css';

const OperatorDashboard = () => {
  const { user, logout } = useAuth();

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
          <button className="btn-primary">Просмотр карты</button>
          <button className="btn-secondary">Мой профиль</button>
        </div>

        <div className="map-container">
          <h3>Карта</h3>
          <div className="map-placeholder">
            {/* Здесь будет компонент карты */}
            <p>Компонент карты будет здесь</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OperatorDashboard;