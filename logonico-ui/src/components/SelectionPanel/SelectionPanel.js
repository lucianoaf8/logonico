import React, { useEffect, useRef, useState } from 'react';
import { useAppState } from '../../hooks/useAppState';
import ActionButton from '../common/ActionButton';

export default function SelectionPanel() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  const panelRef = useRef();
  const [panelWidth, setPanelWidth] = useState('medium');
  const [maxImages, setMaxImages] = useState(6);
  const [processingState, setProcessingState] = useState({
    downloading: false,
    removingBg: false,
    convertingIco: false
  });
  
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

  const handleDownloadSelected = async () => {
    if (selectedImages.size === 0) return;

    setProcessingState(prev => ({ ...prev, downloading: true }));
    try {
      const imageIds = Array.from(selectedImages);
      const response = await fetch('http://localhost:5000/api/images/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageIds })
      });

      if (response.ok) {
        // Get the blob and create download link
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `selected-images-${new Date().toISOString().slice(0, 10)}.zip`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('Failed to download images');
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download images: ' + error.message);
    } finally {
      setProcessingState(prev => ({ ...prev, downloading: false }));
    }
  };

  const handleRemoveBackground = async () => {
    if (selectedImages.size === 0) return;

    setProcessingState(prev => ({ ...prev, removingBg: true }));
    try {
      const imageIds = Array.from(selectedImages);
      const response = await fetch('http://localhost:5000/api/images/remove-background', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageIds })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Background removed from ${result.processed} images successfully!`);
        // Refresh images to show processed versions
        useImages.refresh();
      } else {
        throw new Error('Failed to remove background');
      }
    } catch (error) {
      console.error('Background removal failed:', error);
      alert('Failed to remove background: ' + error.message);
    } finally {
      setProcessingState(prev => ({ ...prev, removingBg: false }));
    }
  };

  const handleConvertToICO = async () => {
    if (selectedImages.size === 0) return;

    setProcessingState(prev => ({ ...prev, convertingIco: true }));
    try {
      const imageIds = Array.from(selectedImages);
      const response = await fetch('http://localhost:5000/api/images/convert-ico', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageIds })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`${result.converted} images converted to ICO successfully!`);
      } else {
        throw new Error('Failed to convert to ICO');
      }
    } catch (error) {
      console.error('ICO conversion failed:', error);
      alert('Failed to convert to ICO: ' + error.message);
    } finally {
      setProcessingState(prev => ({ ...prev, convertingIco: false }));
    }
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
          <ActionButton 
            onClick={handleDownloadSelected} 
            disabled={!selectedImages.size || processingState.downloading}
          >
            {processingState.downloading ? '⏳ Downloading...' : '📥 Download'}
          </ActionButton>
          <ActionButton 
            onClick={handleRemoveBackground} 
            disabled={!selectedImages.size || processingState.removingBg}
          >
            {processingState.removingBg ? '⏳ Processing...' : '🎭 Remove BG'}
          </ActionButton>
          <ActionButton 
            onClick={handleConvertToICO} 
            disabled={!selectedImages.size || processingState.convertingIco}
          >
            {processingState.convertingIco ? '⏳ Converting...' : '🔄 To ICO'}
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