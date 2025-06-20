import { useEffect, useRef } from 'react';

export default function ResizeHandle() {
  const handle = useRef();
  useEffect(()=>{
    const h = handle.current;
    let isResizing=false, startX=0, startCols;
    const container = document.querySelector('.container');
    const onMouseDown = e=>{ isResizing=true; startX=e.clientX; startCols=getComputedStyle(container).gridTemplateColumns.split(' ').map(Number); document.body.style.cursor='col-resize'; };
    const onMouseMove = e=>{
      if(!isResizing) return;
      const dx = e.clientX - startX;
      const [a, g, s ] = startCols;
      const newGallery = g + dx;
      const newSel     = s - dx;
      container.style.gridTemplateColumns = `${a}px ${newGallery}px ${newSel}px`;
      h.style.left = (a+newGallery+1)+'px';
    };
    const onMouseUp = ()=>{ isResizing=false; document.body.style.cursor=''; };
    h.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return ()=>{
      h.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  },[]);
  return <div ref={handle} className="resize-handle" />;
}
