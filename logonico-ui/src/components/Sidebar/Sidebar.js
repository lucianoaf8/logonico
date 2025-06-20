import React, { useState } from 'react';
import { useAppState } from '../../hooks/useAppState';
import RealTimeProgress from './RealTimeProgress';
import WorkflowModal from './WorkflowModal';
import useImages from '../../hooks/useImages';

export default function Sidebar() {
  const { stats, logs } = useAppState();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const totalImages = stats.total_images || 0;
  const providers = stats.providers || {};
  const models = stats.models || {};

  const handleRunWorkflow = async (config) => {
    try {
      // Step 1: Archive current images
      await fetch('http://localhost:5000/api/workflow/archive', {
        method: 'POST'
      });

      // Step 2: Clear gallery
      useImages.refresh();

      // Step 3: Start workflow
      const response = await fetch('http://localhost:5000/api/workflow/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        throw new Error('Failed to start workflow');
      }

      console.log('Workflow started successfully');
    } catch (error) {
      console.error('Workflow start failed:', error);
      throw error;
    }
  };

  return (
    <aside className="sidebar">
      <div className="workflow-section">
        <button 
          className="workflow-trigger-button"
          onClick={() => setIsModalOpen(true)}
        >
          ▶️ New Workflow
        </button>
      </div>
      <RealTimeProgress />
      <div className="model-status">
        <div className="status-section">
          <div className="status-title">📊 Statistics</div>
          <div className="status-stats">
            <div className="stat-item">
              <span className="stat-label">Total Images</span>
              <span className="stat-value">{totalImages}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Providers</span>
              <span className="stat-value">{Object.keys(providers).length}/4</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Models</span>
              <span className="stat-value">{Object.keys(models).length}</span>
            </div>
          </div>
        </div>

        <div className="status-section">
          <div className="status-title">🤖 Providers</div>
          <div className="provider-grid">
            {Object.entries(providers).map(([name, count]) => (
              <div key={name} className="provider-item">
                <div className="provider-dot active"></div>
                <span className="provider-name">{name}</span>
                <span className="provider-count">{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="logs-section">
        <div className="logs-header">
          <div className="status-title">📄 Recent Logs</div>
        </div>
        <div className="logs-content">
          {logs.slice(0, 10).map((log, index) => (
            <div key={index} className="log-entry">
              <span className="log-time">{log.time}</span>
              <span className="log-status">{log.status}</span>
              <span className="log-message">{log.message}</span>
            </div>
          ))}
          {!logs.length && (
            <div className="loading">No logs available</div>
          )}
        </div>
      </div>

      <WorkflowModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onRunWorkflow={handleRunWorkflow}
      />
    </aside>
  );
}