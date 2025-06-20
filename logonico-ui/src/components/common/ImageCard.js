import React from 'react';

export default function ImageCard({ img, selected, onClick }) {
  return (
    <div 
      className={`image-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
      title={`${img.prompt_id} - ${img.provider}:${img.model}`}
    >
      <img 
        src={img.url} 
        alt={img.prompt_id}
        className="image-display"
        loading="lazy"
      />
      {selected && (
        <div className="selection-indicator">
          ✓
        </div>
      )}
      <div className="image-overlay">
        <div className="image-info">
          <div className="image-provider">{img.provider}</div>
          <div className="image-size">{img.size_mb}MB</div>
        </div>
      </div>
    </div>
  );
}