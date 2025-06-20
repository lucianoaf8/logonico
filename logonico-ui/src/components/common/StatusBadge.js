// components/common/StatusBadge.js
import React from 'react';
import styled, { keyframes } from 'styled-components';

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
`;

const Badge = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: ${props => {
    switch(props.size) {
      case 'small': return '2px 6px';
      case 'large': return '6px 12px';
      default: return '4px 8px';
    }
  }};
  border-radius: 4px;
  font-size: ${props => {
    switch(props.size) {
      case 'small': return '10px';
      case 'large': return '14px';
      default: return '11px';
    }
  }};
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
  
  background: ${props => {
    switch(props.variant) {
      case 'success':
        return 'rgba(0, 217, 255, 0.1)';
      case 'error':
        return 'rgba(255, 85, 85, 0.1)';
      case 'warning':
        return 'rgba(255, 193, 7, 0.1)';
      case 'processing':
        return 'rgba(255, 140, 0, 0.1)';
      case 'info':
        return 'rgba(99, 102, 241, 0.1)';
      default:
        return 'rgba(139, 148, 158, 0.1)';
    }
  }};
  
  color: ${props => {
    switch(props.variant) {
      case 'success':
        return 'var(--success)';
      case 'error':
        return 'var(--error)';
      case 'warning':
        return 'var(--warning)';
      case 'processing':
        return 'var(--processing)';
      case 'info':
        return '#6366F1';
      default:
        return 'var(--text-secondary)';
    }
  }};
  
  border: 1px solid ${props => {
    switch(props.variant) {
      case 'success':
        return 'rgba(0, 217, 255, 0.2)';
      case 'error':
        return 'rgba(255, 85, 85, 0.2)';
      case 'warning':
        return 'rgba(255, 193, 7, 0.2)';
      case 'processing':
        return 'rgba(255, 140, 0, 0.2)';
      case 'info':
        return 'rgba(99, 102, 241, 0.2)';
      default:
        return 'var(--border)';
    }
  }};
  
  ${props => props.pulsing && `
    animation: ${pulse} 2s infinite;
  `}
`;

const StatusIcon = styled.span`
  font-size: ${props => props.size === 'small' ? '8px' : '10px'};
  line-height: 1;
`;

const StatusBadge = ({ 
  variant = 'default', 
  size = 'medium',
  children,
  icon,
  pulsing = false,
  className 
}) => {
  const getDefaultIcon = (variant) => {
    switch(variant) {
      case 'success': return '✓';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'processing': return '⏳';
      case 'info': return 'ℹ️';
      default: return null;
    }
  };

  const displayIcon = icon !== undefined ? icon : getDefaultIcon(variant);

  return (
    <Badge 
      variant={variant} 
      size={size} 
      pulsing={pulsing}
      className={className}
    >
      {displayIcon && (
        <StatusIcon size={size}>
          {displayIcon}
        </StatusIcon>
      )}
      {children}
    </Badge>
  );
};

// Provider status component
const ProviderContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ProviderDot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch(props.status) {
      case 'active': return 'var(--success)';
      case 'failed': return 'var(--error)';
      case 'warning': return 'var(--warning)';
      case 'disabled': return 'var(--text-secondary)';
      default: return 'var(--border)';
    }
  }};
  
  ${props => props.status === 'active' && `
    animation: ${pulse} 2s infinite;
  `}
`;

export const ProviderStatus = ({ providers, showText = true }) => {
  const getStatusText = (providers) => {
    const active = providers.filter(p => p.status === 'active').length;
    const total = providers.length;
    return `${active}/${total} Providers`;
  };

  return (
    <ProviderContainer>
      <div style={{ display: 'flex', gap: '4px' }}>
        {providers.map((provider, index) => (
          <ProviderDot 
            key={provider.name || index}
            status={provider.status}
            title={`${provider.name}: ${provider.status}`}
          />
        ))}
      </div>
      {showText && (
        <span style={{ 
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: '14px',
          color: 'var(--text-secondary)'
        }}>
          {getStatusText(providers)}
        </span>
      )}
    </ProviderContainer>
  );
};

// Predefined status badges
export const SuccessBadge = ({ children, ...props }) => (
  <StatusBadge variant="success" {...props}>{children || 'Success'}</StatusBadge>
);

export const ErrorBadge = ({ children, ...props }) => (
  <StatusBadge variant="error" {...props}>{children || 'Failed'}</StatusBadge>
);

export const ProcessingBadge = ({ children, ...props }) => (
  <StatusBadge variant="processing" pulsing {...props}>{children || 'Processing'}</StatusBadge>
);

export const CompleteBadge = ({ children, ...props }) => (
  <StatusBadge variant="success" {...props}>{children || 'Complete'}</StatusBadge>
);

export default StatusBadge;