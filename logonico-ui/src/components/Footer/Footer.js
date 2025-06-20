import React from 'react';
import { useAppState } from '../../hooks/useAppState';
import useImages from '../../hooks/useImages';
import useStats from '../../hooks/useStats';
import useLogs from '../../hooks/useLogs';

export default function Footer() {
  const { stats, selectedImages } = useAppState();
  const totalGenerated = stats.total_images || 0;
  const providersUsed  = Object.keys(stats.providers||{}).length;
  const totalSize      = stats.totalSize || 0;
  const successRate    = stats.success_rate || 100;

  const handleRefresh = () => {
    useImages.refresh();
    useStats.refresh();
    useLogs.refresh();
  };
  const handleOpenFolder = () => {
    // placeholder: backend must implement actual folder open
    alert('Opening output folder…');
  };
  const handleDownload = () => {
    if (!selectedImages.size) {
      alert('No images selected');
      return;
    }
    alert(`Download ${selectedImages.size} selected images?`);
  };
  const handleViewLogs = () => {
    window.open('/api/logs', '_blank');
  };

  return (
    <footer className="footer">
      <div className="main-progress">
        <div className="main-progress-text">
          <span><strong>Generation:</strong> Complete</span>
          <div className="progress-stats">
            <span>📸 {totalGenerated} images</span>
            <span>🎯 {providersUsed} providers</span>
            <span>📁 {totalSize} MB</span>
          </div>
        </div>
        <div className="main-progress-bar">
          <div
            className="main-progress-fill"
            style={{ width: `${successRate}%` }}
          />
        </div>
      </div>

      <div className="controls">
        <button className="control-btn primary" onClick={handleRefresh}>
          🔄 Refresh
        </button>
        <button className="control-btn" onClick={handleOpenFolder}>
          📁 Open Folder
        </button>
        <button className="control-btn" onClick={handleDownload}>
          💾 Download Selected
        </button>
        <button className="control-btn" onClick={handleViewLogs}>
          📊 View Logs
        </button>
      </div>
    </footer>
  );
}
