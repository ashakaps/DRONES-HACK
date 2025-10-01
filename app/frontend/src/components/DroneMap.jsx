// components/DroneMap.jsx
import React, { useEffect, useRef } from 'react';
import './DroneMap.css';

const DroneMap = ({ 
  containerId = "drone-map-container",
  className = "",
  onMapReady,
  onRegionSelect,
  onCitySelect 
}) => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const isInitializedRef = useRef(false);

  useEffect(() => {
    if (isInitializedRef.current) return;

    const initMap = async () => {
      // Динамически загружаем Leaflet
      await loadLeaflet();
      
      // Инициализация карты
      const map = L.map(containerId).setView([55.7558, 37.6173], 10);
      
      // Добавляем слой карты
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);

      mapInstanceRef.current = map;
      isInitializedRef.current = true;

      // Колбэк когда карта готова
      if (onMapReady) {
        onMapReady(map);
      }
    };

    initMap();

    return () => {
      // Очистка при размонтировании
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
      }
    };
  }, [containerId, onMapReady]);

  const loadLeaflet = () => {
    return new Promise((resolve) => {
      if (window.L) {
        resolve();
        return;
      }

      // Загружаем Leaflet CSS
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      link.crossOrigin = '';
      document.head.appendChild(link);

      // Загружаем Leaflet JS
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
      script.crossOrigin = '';
      script.onload = resolve;
      document.head.appendChild(script);
    });
  };

  return (
    <div 
      id={containerId} 
      className={`drone-map-container ${className}`}
      ref={mapRef}
    />
  );
};

export default DroneMap;