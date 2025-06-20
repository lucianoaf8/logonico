import React from 'react';

export default function ActionButton({ onClick, disabled, children, className, ...props }) {
  return (
    <button 
      className={`action-btn ${className || ''} ${disabled ? 'disabled' : ''}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}