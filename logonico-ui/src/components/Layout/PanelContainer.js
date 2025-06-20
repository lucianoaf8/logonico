// components/Layout/PanelContainer.js
import React, { forwardRef } from 'react';
import styled from 'styled-components';
import { useResizePanel } from '../../hooks/useResizePanel';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  position: relative;
  transition: ${props => props.isResizing ? 'none' : 'width 0.2s ease'};
  width: ${props => props.width ? `${props.width}px` : 'auto'};
  min-width: ${props => props.minWidth ? `${props.minWidth}px` : '200px'};
  max-width: ${props => props.maxWidth ? `${props.maxWidth}px` : '800px'};
`;

const ResizeHandle = styled.div`
  position: absolute;
  top: 0;
  bottom: 0;
  width: 4px;
  background: ${props => props.isResizing ? 'var(--accent-blue)' : 'var(--border)'};
  cursor: col-resize;
  z-index: 1000;
  transition: ${props => props.isResizing ? 'none' : 'background-color 0.2s ease'};
  
  ${props => props.position === 'left' && `
    left: -2px;
  `}
  
  ${props => props.position === 'right' && `
    right: -2px;
  `}
  
  &:hover {
    background: var(--accent-blue);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    width: 8px;
    left: -2px;
  }
`;

const PanelHeader = styled.div`
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 60px;
`;

const PanelTitle = styled.h3`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
`;

const PanelControls = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PanelContent = styled.div`
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const PanelFooter = styled.div`
  padding: 12px 20px;
  border-top: 1px solid var(--border);
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 48px;
`;

const PanelContainer = forwardRef(({
  children,
  title,
  controls,
  footer,
  resizable = false,
  resizePosition = 'right',
  defaultWidth = 320,
  minWidth = 200,
  maxWidth = 600,
  onResize,
  className,
  ...props
}, ref) => {
  const resizePanel = useResizePanel({
    defaultWidth,
    minWidth,
    maxWidth,
    onResize
  });

  const containerProps = resizable ? {
    ref: resizePanel.containerRef,
    width: resizePanel.panelWidth,
    isResizing: resizePanel.isResizing,
    minWidth,
    maxWidth
  } : {};

  return (
    <Container 
      ref={ref}
      className={className}
      {...containerProps}
      {...props}
    >
      {title && (
        <PanelHeader>
          <PanelTitle>{title}</PanelTitle>
          {controls && (
            <PanelControls>{controls}</PanelControls>
          )}
        </PanelHeader>
      )}
      
      <PanelContent>
        {children}
      </PanelContent>
      
      {footer && (
        <PanelFooter>
          {footer}
        </PanelFooter>
      )}
      
      {resizable && (
        <ResizeHandle
          ref={resizePanel.resizeRef}
          position={resizePosition}
          isResizing={resizePanel.isResizing}
          onMouseDown={resizePanel.handleMouseDown}
        />
      )}
    </Container>
  );
});

PanelContainer.displayName = 'PanelContainer';

// Specialized panel types
export const ResizablePanel = ({ children, ...props }) => (
  <PanelContainer resizable {...props}>
    {children}
  </PanelContainer>
);

export const SidePanel = ({ children, ...props }) => (
  <PanelContainer 
    resizable
    resizePosition="right"
    defaultWidth={280}
    minWidth={200}
    maxWidth={400}
    {...props}
  >
    {children}
  </PanelContainer>
);

export const SelectionPanel = ({ children, ...props }) => (
  <PanelContainer
    resizable
    resizePosition="left"
    defaultWidth={400}
    minWidth={300}
    maxWidth={600}
    {...props}
  >
    {children}
  </PanelContainer>
);

// Panel with collapsible functionality
export const CollapsiblePanel = ({ 
  children, 
  collapsed = false, 
  onToggleCollapse,
  ...props 
}) => {
  const handleToggle = () => {
    if (onToggleCollapse) {
      onToggleCollapse(!collapsed);
    }
  };

  const controls = (
    <button
      onClick={handleToggle}
      style={{
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: 'var(--text-secondary)',
        fontSize: '14px',
        padding: '4px'
      }}
    >
      {collapsed ? '▶' : '▼'}
    </button>
  );

  return (
    <PanelContainer controls={controls} {...props}>
      {!collapsed && children}
    </PanelContainer>
  );
};

// Panel with size indicator
export const ResponsivePanel = ({ children, ...props }) => {
  const resizePanel = useResizePanel(props);
  
  const sizeIndicator = (
    <div style={{
      fontSize: '12px',
      color: 'var(--text-secondary)',
      fontFamily: 'JetBrains Mono, monospace'
    }}>
      {resizePanel.panelWidth}px ({resizePanel.panelSize})
    </div>
  );

  return (
    <PanelContainer 
      resizable
      footer={sizeIndicator}
      onResize={resizePanel.setWidth}
      {...props}
    >
      {children}
    </PanelContainer>
  );
};

export default PanelContainer;