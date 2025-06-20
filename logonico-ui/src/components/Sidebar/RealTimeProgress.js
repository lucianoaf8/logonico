import React, { useState, useEffect } from 'react';

export default function RealTimeProgress() {
  const [progress, setProgress] = useState({
    status: 'complete',
    total_tasks: 1,
    completed: 1,
    success_rate: 100.0,
    current_prompt: null,
    prompt_progress: null,
    current_model: null,
    model_progress: null,
    endpoint: null,
    latest_image: null
  });

  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    let pollInterval;

    const pollProgress = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/progress');
        if (response.ok) {
          const data = await response.json();
          setProgress(data);
          
          // Start/stop polling based on status
          if (data.status === 'running' && !isPolling) {
            setIsPolling(true);
          } else if (data.status === 'complete' && isPolling) {
            setIsPolling(false);
          }
        }
      } catch (error) {
        console.error('Failed to fetch progress:', error);
      }
    };

    // Initial poll
    pollProgress();

    // Set up polling interval
    pollInterval = setInterval(pollProgress, 1000);

    return () => {
      clearInterval(pollInterval);
    };
  }, [isPolling]);

  const isRunning = progress.status === 'running';
  const progressPercent = progress.total_tasks > 0 
    ? Math.round((progress.completed / progress.total_tasks) * 100)
    : 100;

  return (
    <div className="real-time-progress">
      <div className="status-section">
        <div className="status-title">
          {isRunning ? '🔄 Generation Running' : '✅ Generation Complete'}
        </div>
        
        {isRunning && progress.current_prompt && (
          <div className="current-task">
            <div className="task-item">
              <span className="task-label">Prompt:</span>
              <span className="task-value">{progress.current_prompt}</span>
              {progress.prompt_progress && (
                <span className="task-counter">
                  ({progress.prompt_progress.current}/{progress.prompt_progress.total})
                </span>
              )}
            </div>
            
            {progress.current_model && (
              <div className="task-item">
                <span className="task-label">Model:</span>
                <span className="task-value">{progress.current_model}</span>
                {progress.model_progress && (
                  <span className="task-counter">
                    ({progress.model_progress.current}/{progress.model_progress.total})
                  </span>
                )}
              </div>
            )}
            
            {progress.endpoint && (
              <div className="task-item">
                <span className="task-label">Endpoint:</span>
                <span className="task-value">{progress.endpoint}</span>
              </div>
            )}
          </div>
        )}
        
        <div className="progress-container">
          <div className="progress-text">
            <span>Progress: {progress.completed}/{progress.total_tasks}</span>
            <span>{progressPercent}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <div className="progress-stats">
            <span>Success Rate: {progress.success_rate}%</span>
          </div>
        </div>
        
        {progress.latest_image && (
          <div className="latest-image">
            <div className="latest-label">Latest Generated:</div>
            <div className="latest-filename">{progress.latest_image}</div>
          </div>
        )}
      </div>
    </div>
  );
}