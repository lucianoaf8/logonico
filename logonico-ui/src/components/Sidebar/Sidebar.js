import React from 'react';
import { useAppState } from '../../hooks/useAppState';

export default function Sidebar() {
  const { stats, logs } = useAppState();

  return (
    <aside className="sidebar">
      <div className="model-status">
        <div className="status-section">
          <div className="status-title">🤖 GENERATION STATUS</div>
          <div className="status-value">Total Images: <strong>{stats.total_images}</strong></div>
          <div className="status-value">Providers: <strong>{Object.keys(stats.providers||{}).length}</strong></div>
          <div className="status-value">Models: <strong>{Object.keys(stats.models||{}).length}</strong></div>
          <span className="status-badge complete">Complete</span>
        </div>
        <div className="status-section">
          <div className="status-title">📝 TOP PROMPTS</div>
          <div className="prompt-preview">
            {(stats.prompts||[]).slice(0,3).map(([p,c])=>(
              <div key={p} className="status-value">• {p}: {c}</div>
            ))}
          </div>
        </div>
        <div className="status-section">
          <div className="status-title">🎯 SUCCESS RATE</div>
          <div className="model-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{width: stats.success_rate+'%'}} />
            </div>
            <div className="progress-text">{stats.success_rate}% Success</div>
          </div>
        </div>
        <div className="status-section">
          <div className="status-title">📊 PROVIDERS</div>
          <div id="provider-breakdown">
            {Object.entries(stats.providers||{}).map(([prov,c])=>(
              <div key={prov} className="status-value">• {prov}: {c}</div>
            ))}
          </div>
        </div>
      </div>
      <div className="logs">
        <div className="status-title">📊 RECENT LOGS</div>
        <div className="logs-content">
          {logs.map((l,i)=>(
            <div key={i} className="log-entry">
              <span className="log-time">{l.time}</span>
              <span className="log-status">{l.status}</span>
              <span className="log-message">{l.message}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
