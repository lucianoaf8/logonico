// components/common/LoadingSpinner.js
import React from 'react';
import styled, { keyframes } from 'styled-components';

const spin = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${props => props.size === 'small' ? '20px' : '40px'};
  color: var(--text-secondary);
`;

const Spinner = styled.div`
  width: ${props => {
    switch(props.size) {
      case 'small': return '20px';
      case 'large': return '48px';
      default: return '32px';
    }
  }};
  height: ${props => {
    switch(props.size) {
      case 'small': return '20px';
      case 'large': return '48px';
      default: return '32px';
    }
  }};
  border: 2px solid var(--border);
  border-top: 2px solid var(--accent-blue);
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: ${props => props.showText ? '12px' : '0'};
`;

const DotsSpinner = styled.div`
  display: flex;
  gap: 4px;
  margin-bottom: ${props => props.showText ? '12px' : '0'};
  
  .dot {
    width: 8px;
    height: 8px;
    background: var(--accent-blue);
    border-radius: 50%;
    animation: ${pulse} 1.4s ease-in-out infinite both;
    
    &:nth-child(1) { animation-delay: -0.32s; }
    &:nth-child(2) { animation-delay: -0.16s; }
    &:nth-child(3) { animation-delay: 0; }
  }
`;

const LoadingText = styled.div`
  font-size: ${props => props.size === 'small' ? '12px' : '14px'};
  color: var(--text-secondary);
  text-align: center;
`;

const LoadingSpinner = ({ 
  size = 'medium', 
  text = 'Loading...', 
  showText = true,
  type = 'spinner' // 'spinner' or 'dots'
}) => {
  return (
    <SpinnerContainer size={size}>
      {type === 'dots' ? (
        <DotsSpinner showText={showText}>
          <div className="dot" />
          <div className="dot" />
          <div className="dot" />
        </DotsSpinner>
      ) : (
        <Spinner size={size} showText={showText} />
      )}
      
      {showText && text && (
        <LoadingText size={size}>{text}</LoadingText>
      )}
    </SpinnerContainer>
  );
};

// Inline loading spinner for buttons and small spaces
export const InlineSpinner = styled.div`
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  display: inline-block;
  margin-right: 8px;
`;

// Loading overlay for components
export const LoadingOverlay = ({ children, isLoading, text = 'Loading...' }) => {
  return (
    <div style={{ position: 'relative' }}>
      {children}
      {isLoading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          borderRadius: '8px'
        }}>
          <LoadingSpinner text={text} />
        </div>
      )}
    </div>
  );
};

export default LoadingSpinner;