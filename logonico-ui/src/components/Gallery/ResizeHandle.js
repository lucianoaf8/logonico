import { useEffect, useRef, useState } from 'react';

export default function ResizeHandle() {
  const handle = useRef();
  const [handlePosition, setHandlePosition] = useState(null);
  
  useEffect(() => {
    const h = handle.current;
    if (!h) return;
    
    let isResizing = false;
    let startX = 0;
    let startCols;
    
    const container = document.querySelector('.container');
    if (!container) return;
    
    // Calculate initial handle position
    const updateHandlePosition = () => {
      const cols = getComputedStyle(container).gridTemplateColumns.split(' ');
      const sidebarWidth = parseFloat(cols[0]) || 280;
      const galleryWidth = parseFloat(cols[1]) || 400;
      setHandlePosition(sidebarWidth + galleryWidth);
    };
    
    updateHandlePosition();
    
    const onMouseDown = (e) => { 
      isResizing = true; 
      startX = e.clientX; 
      startCols = getComputedStyle(container).gridTemplateColumns.split(' ').map(col => parseFloat(col)); 
      document.body.style.cursor = 'col-resize'; 
      document.body.style.userSelect = 'none';
    };
    
    const onMouseMove = (e) => {
      if (!isResizing) return;
      const dx = e.clientX - startX;
      const [a, g, s] = startCols;
      const newGallery = g + dx;
      const newSel = s - dx;
      
      // Enforce minimum widths
      if (newGallery < 300 || newSel < 250) return;
      
      container.style.gridTemplateColumns = `${a}px ${newGallery}px ${newSel}px`;
      
      // Update handle position to follow the gallery edge
      setHandlePosition(a + newGallery);
    };
    
    const onMouseUp = () => { 
      isResizing = false; 
      document.body.style.cursor = ''; 
      document.body.style.userSelect = '';
    };
    
    h.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    
    return () => {
      h.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, []);
  
  return <div ref={handle} className="resize-handle" style={{
    position: 'fixed',
    top: '60px',
    bottom: '80px',
    width: '4px',
    background: 'var(--border)',
    cursor: 'col-resize',
    zIndex: 1000,
    left: handlePosition ? `${handlePosition}px` : '680px',
    transition: 'background-color 0.2s ease'
  }} />;
}