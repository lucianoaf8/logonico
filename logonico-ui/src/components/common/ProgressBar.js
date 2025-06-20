// components/common/ProgressBar.js
import React from 'react';
import styled, { keyframes } from 'styled-components';

const shimmer = keyframes`
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
`;

const ProgressContainer = styled.div`
  width: 100%;
  margin: ${props => props.spacing || '8px 0'};
`;

const ProgressLabel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: ${props => props.size === 'small' ? '12px' : '14px'};
  color: var(--text-primary);
`;

const ProgressTrack = styled.div`
  width: 100%;
  height: ${props => {
    switch(props.size) {
      case 'small': return '4px';
      case 'large': return '12px';
      default: return '8px';
    }
  }};
  background: var(--bg-secondary);
  border-radius: ${props => props.size === 'large' ? '6px' : '4px'};
  overflow: hidden;
  position: relative;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.variant === 'success') return 'var(--success)';
    if (props.variant === 'warning') return 'var(--warning)';
    if (props.variant === 'error') return 'var(--error)';
    return 'linear-gradient(90deg, var(--accent-blue), #0084FF)';
  }};
  border-radius: inherit;
  transition: width 0.5s ease;
  box-shadow: ${props => props.glowing ? 'var(--glow)' : 'none'};
  width: ${props => Math.min(100, Math.max(0, props.percentage))}%;
  
  ${props => props.animated && `
    background-image: linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.1) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.1) 50%,
      rgba(255, 255, 255, 0.1) 75%,
      transparent 75%,
      transparent
    );
    background-size: 20px 20px;
    animation: ${shimmer} 1s linear infinite;
  `}
`;

const ProgressText = styled.span`
  font-weight: 500;
  color: var(--text-secondary);
`;

const ProgressPercentage = styled.span`
  font-weight: 600;
  color: var(--text-primary);
`;

const ProgressBar = ({
  percentage = 0,
  label,
  showPercentage = true,
  size = 'medium',
  variant = 'primary',
  animated = false,
  glowing = true,
  spacing,
  customText
}) => {
  const formatPercentage = (value) => {
    return `${Math.round(value)}%`;
  };

  return (
    <ProgressContainer spacing={spacing}>
      {(label || showPercentage || customText) && (
        <ProgressLabel size={size}>
          <ProgressText>
            {label || ''}
          </ProgressText>
          <ProgressPercentage>
            {customText || (showPercentage ? formatPercentage(percentage) : '')}
          </ProgressPercentage>
        </ProgressLabel>
      )}
      
      <ProgressTrack size={size}>
        <ProgressFill
          percentage={percentage}
          variant={variant}
          animated={animated}
          glowing={glowing}
        />
      </ProgressTrack>
    </ProgressContainer>
  );
};

// Circular progress bar variant
const CircularContainer = styled.div`
  position: relative;
  width: ${props => props.size}px;
  height: ${props => props.size}px;
`;

const CircularSvg = styled.svg`
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
`;

const CircularTrack = styled.circle`
  fill: none;
  stroke: var(--bg-secondary);
  stroke-width: ${props => props.strokeWidth};
`;

const CircularFill = styled.circle`
  fill: none;
  stroke: var(--accent-blue);
  stroke-width: ${props => props.strokeWidth};
  stroke-linecap: round;
  stroke-dasharray: ${props => props.circumference};
  stroke-dashoffset: ${props => props.circumference - (props.percentage / 100) * props.circumference};
  transition: stroke-dashoffset 0.5s ease;
`;

const CircularText = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'JetBrains Mono', monospace;
  font-size: ${props => props.size > 60 ? '14px' : '12px'};
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
`;

export const CircularProgressBar = ({
  percentage = 0,
  size = 80,
  strokeWidth = 8,
  showPercentage = true,
  customText
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;

  return (
    <CircularContainer size={size}>
      <CircularSvg>
        <CircularTrack
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <CircularFill
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          percentage={percentage}
          circumference={circumference}
        />
      </CircularSvg>
      
      {(showPercentage || customText) && (
        <CircularText size={size}>
          {customText || `${Math.round(percentage)}%`}
        </CircularText>
      )}
    </CircularContainer>
  );
};

// Mini progress bar for inline use
export const MiniProgressBar = ({ percentage, width = '100px' }) => (
  <ProgressTrack size="small" style={{ width, margin: 0 }}>
    <ProgressFill percentage={percentage} glowing={false} />
  </ProgressTrack>
);

export default ProgressBar;