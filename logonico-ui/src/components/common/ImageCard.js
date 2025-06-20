import React from 'react';

export default function ImageCard({img,selected,onClick}) {
  return (
    <div
      className={`image-card ${selected?'selected':''}`}
      data-status={img.status}
      data-provider={img.provider}
      onClick={onClick}
      onMouseEnter={()=>{/* could call info hook */}}
      onMouseLeave={()=>{}}
    >
      <img src={img.url} alt={img.prompt_id} className="image-display"
           onError={e=>{e.currentTarget.style.display='none';}}/>
      <div className="image-placeholder">🖼️</div>
    </div>
  );
}
