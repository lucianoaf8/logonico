import React, { useEffect, useRef, useState } from 'react';
import { useAppState } from '../../hooks/useAppState';
import ActionButton from '../common/ActionButton';

export default function SelectionPanel() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  const panelRef = useRef();
  const [panelWidth, setPanelWidth] = useState('medium');
  const [maxImages, setMaxImages] = useState(6);
  
  // Convert Set to Array for filtering and enforce max limit
  const selectedIds = Array.from(selectedImages);
  const selectedData = allImages.filter(img => selectedImages.has(img.id));
  
  // Enforce max images limit - remove oldest if exceeding
  useEffect(() => {
    if (selectedImages.size > maxImages) {
      const selectedArray = Array.from(selectedImages);
      const excess = selectedImages.size - maxImages;
      const newSelection = new Set(selectedArray.slice(excess));
      setSelectedImages(newSelection);
    }
  }, [selectedImages.size, maxImages, selectedImages, setSelectedImages]);

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

  // Monitor panel width changes and calculate max images
  useEffect(() => {
    const updatePanelSize = () => {
      if (panelRef.current) {
        const width = panelRef.current.offsetWidth;
        const height = panelRef.current.offsetHeight;
        
        // Calculate available space for images (minus padding and header)
        const availableWidth = width - 40; // 20px padding on each side
        const availableHeight = height - 140; // header (~100px) + padding
        
        let imageSize, columns, rows, maxImagesCount;
        
        if (width < 300) {
          setPanelWidth('small');
          imageSize = availableWidth; // Single column
          columns = 1;
        } else if (width < 400) {
          setPanelWidth('medium');
          imageSize = 150;
          columns = Math.floor((availableWidth + 12) / (imageSize + 12));
        } else if (width < 500) {
          setPanelWidth('large');
          imageSize = 180;
          columns = Math.floor((availableWidth + 12) / (imageSize + 12));
        } else {
          setPanelWidth('xlarge');
          imageSize = 200;
          columns = Math.floor((availableWidth + 12) / (imageSize + 12));
        }
        
        rows = Math.floor((availableHeight + 12) / (imageSize + 12));
        maxImagesCount = Math.max(1, columns * rows);
        
        setMaxImages(maxImagesCount);
      }
    };

    updatePanelSize();
    
    const resizeObserver = new ResizeObserver(updatePanelSize);
    if (panelRef.current) {
      resizeObserver.observe(panelRef.current);
    }

    return () => resizeObserver.disconnect();
  }, []);

  return (
    <aside ref={panelRef} className="selection-panel" data-width={panelWidth}>
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

    </aside>
  );
}