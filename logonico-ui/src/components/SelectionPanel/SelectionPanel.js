import React from 'react';
import { useAppState } from '../../hooks/useAppState';
import ActionButton from '../common/ActionButton';

export default function SelectionPanel() {
  const { allImages, selectedImages, setSelectedImages } = useAppState();
  const selectedData = allImages.filter(img=>selectedImages.has(img.id));

  const toggle = id=>{
    const s=new Set(selectedImages);
    s.has(id)?s.delete(id):s.add(id);
    setSelectedImages(s);
  };

  return (
    <aside className="selection-panel">
      <div className="selection-header">
        <div className="selection-title">
          <span>Selected Images</span>
          <span className="clear-selection" onClick={()=>setSelectedImages(new Set())}>
            Clear All
          </span>
        </div>
        <div className="selection-actions">
          <ActionButton onClick={()=>alert('remove bg')} disabled={!selectedImages.size}>
            🎭 Remove BG
          </ActionButton>
          <ActionButton onClick={()=>alert('to ico')} disabled={!selectedImages.size}>
            🔄 To ICO
          </ActionButton>
        </div>
      </div>

      <div className="selected-images">
        {!selectedData.length
          ? <div className="empty-selection">
              <div className="empty-icon">🖼️</div>
              <div>Click images to select</div>
              <div style={{marginTop:8,fontSize:11}}>
                Compare and process selected images
              </div>
            </div>
          : selectedData.map(img=>(
              <div key={img.id} className="selected-image-card">
                <img src={img.url} alt="" className="selected-image-display"/>
                <div className="selected-image-status">✓</div>
                <div className="remove-selected" onClick={()=>toggle(img.id)}>×</div>
              </div>
            ))
        }
      </div>

      {selectedData.length>0 && (
        <div className="selection-info">
          <div className="info-line"><strong>Selected Image Info:</strong></div>
          <div className="info-line">Name: {selectedData[0].prompt_id}</div>
          <div className="info-line">Model: {selectedData[0].provider}:{selectedData[0].model}</div>
          <div className="info-line">Size: {selectedData[0].size_mb}MB</div>
          <div className="info-line">Date: {selectedData[0].created_at}</div>
        </div>
      )}
    </aside>
  );
}
