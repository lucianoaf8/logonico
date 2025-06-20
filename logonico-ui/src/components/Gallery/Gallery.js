import React from 'react';
import { useAppState } from '../../hooks/useAppState';

export default function Gallery() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  const [filter, setFilter] = React.useState('all');
  const [hoveredImage, setHoveredImage] = React.useState(null);

  const filtered = allImages.filter(img => {
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
    </main>
  );
}