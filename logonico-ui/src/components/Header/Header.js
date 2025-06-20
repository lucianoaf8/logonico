import React from 'react';
import { useAppState } from '../../hooks/useAppState';

export default function Header({ onToggleTheme }) {
  const { selectedImages, stats } = useAppState();
  const selCount = selectedImages.size;
  const provCount = stats.providers?Object.keys(stats.providers).length:0;

  return (
    <header className="header">
      <div className="logo">
        <div className="logo-icon">L</div>
        <span>LogoNico Generator</span>
      </div>
      <div className="header-center">
        <div className="selected-info">
          <span>{selCount} selected</span>
        </div>
        <div className="provider-status">
          <div className="provider-dots">
            {Array.from({length:5}).map((_,i)=>(
              <div key={i} className={i<provCount?'dot':'dot failed'} />
            ))}
          </div>
          <span>{provCount}/4 Providers</span>
        </div>
      </div>
      <div className="header-controls">
        <button className="theme-toggle" onClick={onToggleTheme}>
          {/* icon swap could be handled via useTheme state */}
          🌙
        </button>
        <button className="theme-toggle">⚙️</button>
      </div>
    </header>
  );
}
