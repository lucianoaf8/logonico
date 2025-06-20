import React from 'react';

export default function FilterButton({ active, onClick, label }) {
  return (
    <button 
      className={`filter-btn ${active ? 'active' : ''}`}
      onClick={onClick}
    >
      {label}
    </button>
  );
}