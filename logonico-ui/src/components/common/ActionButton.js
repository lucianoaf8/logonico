import React from 'react';
export default function ActionButton({onClick,disabled,children}) {
  return (
    <button className="action-btn" disabled={disabled} onClick={onClick}>
      {children}
    </button>
  );
}
