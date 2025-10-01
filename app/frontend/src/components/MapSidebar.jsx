// components/MapSidebar.jsx
import React from 'react';
import './MapSidebar.css';

const MapSidebar = ({
  isOpen = false,
  title = "Регион",
  content = "Здесь будет информация о регионе...",
  position = "right",
  onClose,
  children,
  className = ""
}) => {
  if (!isOpen) return null;

  return (
    <div className={`map-sidebar map-sidebar-${position} ${className}`}>
      <div className="sidebar-header">
        <span className="sidebar-title">{title}</span>
        <button 
          className="sidebar-close"
          onClick={onClose}
        >
          ×
        </button>
      </div>
      <div className="sidebar-content">
        {children || content}
      </div>
    </div>
  );
};

export default MapSidebar;