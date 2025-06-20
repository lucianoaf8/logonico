// components/Gallery/ProviderDots.js
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

const ProviderContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
`;

const DotsContainer = styled.div`
  display: flex;
  gap: 4px;
`;

const Dot = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch(props.status) {
      case 'active':
        return 'var(--success)';
      case 'failed':
      case 'error':
        return 'var(--error)';
      case 'warning':
      case 'rate-limited':
        return 'var(--warning)';
      case 'disabled':
        return 'var(--text-secondary)';
      case 'processing':
        return 'var(--processing)';
      default:
        return 'var(--border)';
    }
  }};
  
  ${props => props.status === 'active' && `
    animation: ${pulse} 2s infinite;
  `}
  
  ${props => props.status === 'processing' && `
    animation: ${pulse} 1s infinite;
  `}
  
  cursor: pointer;
  transition: transform 0.2s ease;
  
  &:hover {
    transform: scale(1.2);
  }
`;

const StatusText = styled.span`
  color: var(--text-secondary);
`;

const ProviderTooltip = styled.div`
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  white-space: nowrap;
  z-index: 1000;
  margin-bottom: 4px;
  
  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: var(--border);
  }
`;

const DotWrapper = styled.div`
  position: relative;
  
  &:hover .tooltip {
    opacity: 1;
    visibility: visible;
  }
  
  .tooltip {
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s ease;
  }
`;

const PROVIDER_INFO = {
  together_ai: {
    name: 'Together AI',
    color: '#00D9FF'
  },
  replicate: {
    name: 'Replicate',
    color: '#00D9FF'
  },
  openai: {
    name: 'OpenAI',
    color: '#00D9FF'
  },
  fal_ai: {
    name: 'Fal.ai',
    color: '#00D9FF'
  }
};

const ProviderDots = ({ 
  providers = [], 
  showText = true,
  showTooltips = true,
  className,
  onProviderClick 
}) => {
  // Ensure we have consistent provider data
  const normalizedProviders = providers.map(provider => {
    if (typeof provider === 'string') {
      return { name: provider, status: 'unknown' };
    }
    return {
      name: provider.name || provider.provider || 'unknown',
      status: provider.status || 'unknown',
      count: provider.count || 0,
      ...provider
    };
  });

  // Calculate status text
  const getStatusText = () => {
    const active = normalizedProviders.filter(p => p.status === 'active').length;
    const total = normalizedProviders.length;
    return `${active}/${total} Providers`;
  };

  const handleProviderClick = (provider) => {
    if (onProviderClick) {
      onProviderClick(provider);
    }
  };

  return (
    <ProviderContainer className={className}>
      <DotsContainer>
        {normalizedProviders.map((provider, index) => {
          const providerInfo = PROVIDER_INFO[provider.name] || { name: provider.name };
          
          return (
            <DotWrapper key={provider.name || index}>
              <Dot
                status={provider.status}
                onClick={() => handleProviderClick(provider)}
                title={showTooltips ? undefined : `${providerInfo.name}: ${provider.status}`}
              />
              
              {showTooltips && (
                <ProviderTooltip className="tooltip">
                  <div style={{ fontWeight: '600' }}>{providerInfo.name}</div>
                  <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>
                    Status: {provider.status}
                    {provider.count > 0 && ` • ${provider.count} images`}
                  </div>
                </ProviderTooltip>
              )}
            </DotWrapper>
          );
        })}
      </DotsContainer>
      
      {showText && (
        <StatusText>{getStatusText()}</StatusText>
      )}
    </ProviderContainer>
  );
};

// Preset configurations
export const defaultProviders = [
  { name: 'together_ai', status: 'active' },
  { name: 'replicate', status: 'active' },
  { name: 'openai', status: 'failed' },
  { name: 'fal_ai', status: 'active' }
];

// Simple version without tooltips
export const SimpleProviderDots = ({ providers, ...props }) => (
  <ProviderDots 
    providers={providers} 
    showTooltips={false} 
    showText={false}
    {...props} 
  />
);

// Provider status from API data
export const ProviderDotsFromStats = ({ stats, ...props }) => {
  const providers = Object.entries(stats?.providers || {}).map(([name, count]) => ({
    name,
    status: count > 0 ? 'active' : 'failed',
    count
  }));

  return <ProviderDots providers={providers} {...props} />;
};

export default ProviderDots;