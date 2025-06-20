// hooks/useResizePanel.js
import { useState, useEffect, useRef, useCallback } from 'react';

export const useResizePanel = ({ 
  minWidth = 280, 
  maxWidth = 600, 
  defaultWidth = 400,
  onResize 
} = {}) => {
  const [panelWidth, setPanelWidth] = useState(defaultWidth);
  const [isResizing, setIsResizing] = useState(false);
  const [panelSize, setPanelSize] = useState('medium');
  
  const resizeRef = useRef(null);
  const containerRef = useRef(null);
  const startXRef = useRef(0);
  const startWidthRef = useRef(defaultWidth);

  // Calculate panel size category for responsive grid
  const updatePanelSize = useCallback((width) => {
    if (width < 300) {
      setPanelSize('small');
    } else if (width < 400) {
      setPanelSize('medium');
    } else if (width < 500) {
      setPanelSize('large');
    } else {
      setPanelSize('xlarge');
    }
  }, []);

  // Handle mouse down on resize handle
  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
    startXRef.current = e.clientX;
    startWidthRef.current = panelWidth;
    
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  }, [panelWidth]);

  // Handle mouse move during resize
  const handleMouseMove = useCallback((e) => {
    if (!isResizing) return;

    const deltaX = startXRef.current - e.clientX;
    const newWidth = startWidthRef.current + deltaX;
    
    // Enforce min/max constraints
    const constrainedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    
    setPanelWidth(constrainedWidth);
    updatePanelSize(constrainedWidth);
    
    if (onResize) {
      onResize(constrainedWidth);
    }
  }, [isResizing, minWidth, maxWidth, updatePanelSize, onResize]);

  // Handle mouse up to end resize
  const handleMouseUp = useCallback(() => {
    if (!isResizing) return;
    
    setIsResizing(false);
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
  }, [isResizing]);

  // Set up event listeners
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // Handle window resize to maintain proportions
  useEffect(() => {
    const handleWindowResize = () => {
      const windowWidth = window.innerWidth;
      const maxAllowedWidth = windowWidth * 0.5; // Max 50% of window
      const minAllowedWidth = windowWidth * 0.2; // Min 20% of window
      
      const constrainedWidth = Math.max(
        minAllowedWidth, 
        Math.min(maxAllowedWidth, panelWidth)
      );
      
      if (constrainedWidth !== panelWidth) {
        setPanelWidth(constrainedWidth);
        updatePanelSize(constrainedWidth);
        
        if (onResize) {
          onResize(constrainedWidth);
        }
      }
    };

    window.addEventListener('resize', handleWindowResize);
    return () => window.removeEventListener('resize', handleWindowResize);
  }, [panelWidth, updatePanelSize, onResize]);

  // Initialize panel size on mount
  useEffect(() => {
    updatePanelSize(panelWidth);
  }, [updatePanelSize, panelWidth]);

  // Reset to default width
  const resetWidth = useCallback(() => {
    setPanelWidth(defaultWidth);
    updatePanelSize(defaultWidth);
    
    if (onResize) {
      onResize(defaultWidth);
    }
  }, [defaultWidth, updatePanelSize, onResize]);

  // Programmatically set width
  const setWidth = useCallback((width) => {
    const constrainedWidth = Math.max(minWidth, Math.min(maxWidth, width));
    setPanelWidth(constrainedWidth);
    updatePanelSize(constrainedWidth);
    
    if (onResize) {
      onResize(constrainedWidth);
    }
  }, [minWidth, maxWidth, updatePanelSize, onResize]);

  return {
    // State
    panelWidth,
    isResizing,
    panelSize,
    
    // Refs for DOM elements
    resizeRef,
    containerRef,
    
    // Event handlers
    handleMouseDown,
    
    // Utility functions
    resetWidth,
    setWidth,
    
    // CSS styles for dynamic layout
    panelStyle: {
      width: `${panelWidth}px`,
      transition: isResizing ? 'none' : 'width 0.2s ease'
    },
    
    resizeHandleStyle: {
      cursor: isResizing ? 'col-resize' : 'col-resize',
      backgroundColor: isResizing ? 'var(--accent-blue)' : 'var(--border)',
      transition: isResizing ? 'none' : 'background-color 0.2s ease'
    }
  };
};

export default useResizePanel;