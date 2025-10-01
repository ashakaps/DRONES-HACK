// components/InfoPanels.jsx
import React from 'react';
import './InfoPanels.css';

const InfoPanel = ({
  id,
  title,
  content,
  position = "left-top",
  isOpen = true,
  onClose,
  children
}) => {
  if (!isOpen) return null;

  return (
    <div className={`info-panel info-panel-${position}`} id={id}>
      <div className="panel-header">
        <span className="panel-title">{title}</span>
        {onClose && (
          <button className="panel-close" onClick={onClose}>
            ×
          </button>
        )}
      </div>
      <div className="panel-content">
        {children || content}
      </div>
    </div>
  );
};

const InfoPanels = ({ panels = [], onPanelClose }) => {
  return (
    <>
      {panels.map(panel => (
        <InfoPanel
          key={panel.id}
          id={panel.id}
          title={panel.title}
          content={panel.content}
          position={panel.position}
          isOpen={panel.isOpen}
          onClose={() => onPanelClose?.(panel.id)}
        >
          {panel.children}
        </InfoPanel>
      ))}
    </>
  );
};

export default InfoPanels;