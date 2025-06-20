// components/Gallery/LogEntry.js
import React from 'react';
import styled, { keyframes } from 'styled-components';

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`;

const LogEntryContainer = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 4px;
  padding: 2px 0;
  animation: ${slideIn} 0.3s ease;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  line-height: 1.6;
  
  &:hover {
    background: rgba(255, 255, 255, 0.02);
    border-radius: 4px;
    padding: 2px 4px;
    margin: 2px -4px;
  }
`;

const LogTime = styled.span`
  color: var(--text-secondary);
  min-width: 55px;
  flex-shrink: 0;
  font-size: 11px;
`;

const LogStatus = styled.span`
  min-width: 16px;
  flex-shrink: 0;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const LogMessage = styled.span`
  color: var(--text-primary);
  flex: 1;
  word-break: break-word;
  
  /* Highlight important parts */
  .highlight {
    color: var(--accent-blue);
    font-weight: 500;
  }
  
  .error {
    color: var(--error);
  }
  
  .success {
    color: var(--success);
  }
  
  .warning {
    color: var(--warning);
  }
`;

const LogBadge = styled.span`
  background: ${props => {
    switch(props.type) {
      case 'success': return 'rgba(0, 217, 255, 0.1)';
      case 'error': return 'rgba(255, 85, 85, 0.1)';
      case 'warning': return 'rgba(255, 193, 7, 0.1)';
      default: return 'rgba(139, 148, 158, 0.1)';
    }
  }};
  color: ${props => {
    switch(props.type) {
      case 'success': return 'var(--success)';
      case 'error': return 'var(--error)';
      case 'warning': return 'var(--warning)';
      default: return 'var(--text-secondary)';
    }
  }};
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 500;
  margin-left: 4px;
`;

const LogEntry = ({ 
  time, 
  status, 
  message, 
  level = 'info',
  className,
  onClick 
}) => {
  // Parse and enhance the message
  const parseMessage = (msg) => {
    if (!msg) return msg;
    
    // Highlight model names, prompt IDs, and important keywords
    const enhanced = msg
      .replace(/\b(SUCCESS|FAILED|ERROR|WARNING|INFO)\b/g, '<span class="highlight">$1</span>')
      .replace(/\b(flux_dev|dalle3|galleri5|ideogram|recraft)\w*/g, '<span class="highlight">$1</span>')
      .replace(/\b(Rate limit|429|401|403|500)\b/g, '<span class="error">$1</span>')
      .replace(/\b(\d+\/\d+|\d+%)\b/g, '<span class="success">$1</span>');
    
    return enhanced;
  };

  const getStatusIcon = (status, level) => {
    if (status) return status;
    
    switch(level?.toLowerCase()) {
      case 'success':
      case 'info':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'debug':
        return '🔍';
      default:
        return 'ℹ️';
    }
  };

  const getLogType = (message, level) => {
    if (message?.includes('SUCCESS') || level === 'success') return 'success';
    if (message?.includes('ERROR') || message?.includes('FAILED') || level === 'error') return 'error';
    if (message?.includes('WARNING') || level === 'warning') return 'warning';
    return 'info';
  };

  const formatTime = (timeStr) => {
    if (!timeStr) return '--:--:--';
    
    // If it's already in HH:MM:SS format, return as is
    if (/^\d{2}:\d{2}:\d{2}$/.test(timeStr)) {
      return timeStr;
    }
    
    // If it's a full timestamp, extract time
    try {
      const date = new Date(timeStr);
      return date.toLocaleTimeString('en-US', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    } catch {
      return timeStr.slice(0, 8); // Fallback: take first 8 characters
    }
  };

  const logType = getLogType(message, level);
  const enhancedMessage = parseMessage(message);

  return (
    <LogEntryContainer className={className} onClick={onClick}>
      <LogTime title={time}>
        {formatTime(time)}
      </LogTime>
      
      <LogStatus>
        {getStatusIcon(status, level)}
      </LogStatus>
      
      <LogMessage>
        <span dangerouslySetInnerHTML={{ __html: enhancedMessage }} />
        {(level === 'error' || message?.includes('FAILED')) && (
          <LogBadge type="error">ERROR</LogBadge>
        )}
        {(level === 'warning' || message?.includes('WARNING')) && (
          <LogBadge type="warning">WARN</LogBadge>
        )}
        {(level === 'success' || message?.includes('SUCCESS')) && (
          <LogBadge type="success">OK</LogBadge>
        )}
      </LogMessage>
    </LogEntryContainer>
  );
};

// Specialized log entry types
export const SuccessLogEntry = ({ time, message, ...props }) => (
  <LogEntry 
    time={time} 
    status="✅" 
    message={message} 
    level="success" 
    {...props} 
  />
);

export const ErrorLogEntry = ({ time, message, ...props }) => (
  <LogEntry 
    time={time} 
    status="❌" 
    message={message} 
    level="error" 
    {...props} 
  />
);

export const WarningLogEntry = ({ time, message, ...props }) => (
  <LogEntry 
    time={time} 
    status="⚠️" 
    message={message} 
    level="warning" 
    {...props} 
  />
);

export const InfoLogEntry = ({ time, message, ...props }) => (
  <LogEntry 
    time={time} 
    status="ℹ️" 
    message={message} 
    level="info" 
    {...props} 
  />
);

export default LogEntry;