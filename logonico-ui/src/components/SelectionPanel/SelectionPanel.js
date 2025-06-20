import React from 'react';
import { useAppState } from '../../hooks/useAppState';
import ActionButton from '../common/ActionButton';

export default function SelectionPanel() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  
  // Convert Set to Array for filtering
  const selectedIds = Array.from(selectedImages);
  const selectedData = allImages.filter(img => selectedImages.has(img.id));

  console.log('Selection Debug:', {
    selectedImages: selectedImages,
    selectedIds: selectedIds,
    selectedData: selectedData,
    allImagesCount: allImages.length
  });

  const toggle = id => {
    const s = new Set(selectedImages);
    s.has(id) ? s.delete(id) : s.add(id);
    setSelectedImages(s);
  };

  const clearAll = () => {
    setSelectedImages(new Set());
  };

  return (
    <aside className="selection-panel">
      <div className="selection-header">
        <div className="selection-title">
          <span>Selected Images ({selectedImages.size})</span>
          {selectedImages.size > 0 && (
            <span className="clear-selection" onClick={clearAll}>
              Clear All
            </span>
          )}
        </div>
        <div className="selection-actions">
          <ActionButton onClick={() => alert('Remove background from ' + selectedImages.size + ' images')} disabled={!selectedImages.size}>
            🎭 Remove BG
          </ActionButton>
          <ActionButton onClick={() => alert('Convert ' + selectedImages.size + ' images to ICO')} disabled={!selectedImages.size}>
            🔄 To ICO
          </ActionButton>
        </div>
      </div>

      <div className="selected-images">
        {!selectedData.length ? (
          <div className="empty-selection">
            <div className="empty-icon">🖼️</div>
            <div>Click images to select</div>
            <div style={{marginTop: 8, fontSize: 11, color: 'var(--text-secondary)'}}>
              Compare and process selected images
            </div>
          </div>
        ) : (
          selectedData.map(img => (
            <div key={img.id} className="selected-image-card">
              <img 
                src={`http://localhost:5000/api/image/${img.filename}`} 
                alt={img.prompt_id} 
                className="selected-image-display"
              />
              <div className="selected-image-status">✓</div>
              <div className="remove-selected" onClick={() => toggle(img.id)} title="Remove from selection">
                ×
              </div>
            </div>
          ))
        )}
      </div>

      {selectedData.length > 0 && (
        <div className="selection-info">
          <div className="info-line"><strong>Selection Info:</strong></div>
          <div className="info-line">Count: {selectedData.length} images</div>
          <div className="info-line">Total Size: {selectedData.reduce((sum, img) => sum + (img.size_mb || 0), 0).toFixed(1)} MB</div>
          {selectedData.length === 1 && (
            <>
              <div className="info-line">Name: {selectedData[0].prompt_id}</div>
              <div className="info-line">Provider: {selectedData[0].provider}</div>
              <div className="info-line">Model: {selectedData[0].model}</div>
            </>
          )}
        </div>
      )}
    </aside>
  );
}