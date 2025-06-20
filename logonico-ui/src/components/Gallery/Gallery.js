import React from 'react';
import { useAppState } from '../../hooks/useAppState';
import ResizeHandle from './ResizeHandle';

export default function Gallery() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  const [filter, setFilter] = React.useState('all');
  const [hoveredImage, setHoveredImage] = React.useState(null);
  const [deletedImages, setDeletedImages] = React.useState(new Set());

  const filtered = allImages.filter(img => {
    if (deletedImages.has(img.id)) return false;
    if (filter === 'all') return true;
    return img.status === filter || img.provider === filter;
  });

  const toggle = id => {
    const s = new Set(selectedImages);
    s.has(id) ? s.delete(id) : s.add(id);
    setSelectedImages(s);
  };

  const handleImageHover = (img) => {
    setHoveredImage(img);
  };

  const handleImageLeave = () => {
    setHoveredImage(null);
  };

  const handleDeleteImage = async (e, img) => {
    e.stopPropagation();
    try {
      const response = await fetch(`http://localhost:5000/api/image/${img.filename}/delete`, {
        method: 'POST'
      });
      if (response.ok) {
        setDeletedImages(prev => new Set([...prev, img.id]));
        // Also remove from selected images if it was selected
        if (selectedImages.has(img.id)) {
          const newSelected = new Set(selectedImages);
          newSelected.delete(img.id);
          setSelectedImages(newSelected);
        }
      }
    } catch (error) {
      console.error('Failed to delete image:', error);
    }
  };

  return (
    <main className="gallery">
      <div className="gallery-header">
        <h2 className="gallery-title">
          Generated Gallery ({filtered.length})
        </h2>
        <div className="gallery-filters">
          {['all', 'success', 'openai', 'replicate', 'together_ai', 'fal_ai']
            .map(f => (
              <button
                key={f}
                className={`filter-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? 'All' : f}
              </button>
            ))
          }
        </div>
      </div>
      
      <div className="gallery-grid">
        {filtered.length ? filtered.map(img => (
          <div
            key={img.id}
            className={`image-card ${selectedImages.has(img.id) ? 'selected' : ''}`}
            onClick={() => toggle(img.id)}
            onMouseEnter={() => handleImageHover(img)}
            onMouseLeave={handleImageLeave}
          >
            <img 
              src={`http://localhost:5000/api/image/${img.filename}`} 
              alt={img.prompt_id}
              className="image-display"
            />
            {selectedImages.has(img.id) && (
              <div className="selection-indicator">✓</div>
            )}
            <button 
              className="delete-button"
              onClick={(e) => handleDeleteImage(e, img)}
              title="Delete image"
            >
              🗑️
            </button>
          </div>
        )) : (
          <div className="loading">No images found</div>
        )}
      </div>

      {/* Image Hover Info Panel */}
      {hoveredImage && (
        <div className={`image-hover-info ${hoveredImage ? 'visible' : ''}`}>
          <div className="hover-info-title">{hoveredImage.prompt_id}</div>
          <div className="hover-info-item">
            <span className="hover-info-label">Provider:</span>
            <span className="hover-info-value">{hoveredImage.provider}</span>
          </div>
          <div className="hover-info-item">
            <span className="hover-info-label">Model:</span>
            <span className="hover-info-value">{hoveredImage.model}</span>
          </div>
          <div className="hover-info-item">
            <span className="hover-info-label">Created:</span>
            <span className="hover-info-value">{hoveredImage.created_at}</span>
          </div>
          <div className="hover-info-item">
            <span className="hover-info-label">Size:</span>
            <span className="hover-info-value">{hoveredImage.size_mb} MB</span>
          </div>
        </div>
      )}
      
      <ResizeHandle />
    </main>
  );
}