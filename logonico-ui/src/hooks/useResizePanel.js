import { useState, useRef, useCallback } from 'react';

export default function useResizePanel({
  defaultWidth = 320,
  minWidth = 200,
  maxWidth = 600,
  onResize
}) {
  const [panelWidth, setPanelWidth] = useState(defaultWidth);
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef();
  const resizeRef = useRef();

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
    
    const startX = e.clientX;
    const startWidth = panelWidth;

    const handleMouseMove = (e) => {
      const deltaX = e.clientX - startX;
      const newWidth = Math.max(minWidth, Math.min(maxWidth, startWidth + deltaX));
      setPanelWidth(newWidth);
      if (onResize) onResize(newWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }, [panelWidth, minWidth, maxWidth, onResize]);

  const setWidth = useCallback((width) => {
    const newWidth = Math.max(minWidth, Math.min(maxWidth, width));
    setPanelWidth(newWidth);
    if (onResize) onResize(newWidth);
  }, [minWidth, maxWidth, onResize]);

  const panelSize = panelWidth < 250 ? 'small' : panelWidth > 450 ? 'large' : 'medium';

  return {
    panelWidth,
    panelSize,
    isResizing,
    containerRef,
    resizeRef,
    handleMouseDown,
    setWidth
  };
}

export { useResizePanel };