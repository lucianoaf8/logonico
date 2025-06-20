import React, { useState, useEffect } from 'react';

export default function WorkflowModal({ isOpen, onClose, onRunWorkflow }) {
  const [config, setConfig] = useState({
    promptFile: 'default',
    models: 'all',
    specificModels: [],
    prompts: 'all', 
    specificPrompts: [],
    removeBackground: true,
    createICO: true
  });

  const [availablePromptFiles, setAvailablePromptFiles] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load available options when modal opens
  useEffect(() => {
    if (isOpen) {
      loadAvailableOptions();
    }
  }, [isOpen]);

  const loadAvailableOptions = async () => {
    try {
      // Get available models
      const modelsResponse = await fetch('http://localhost:5000/api/workflow/models');
      if (modelsResponse.ok) {
        const models = await modelsResponse.json();
        setAvailableModels(models);
      }

      // Get available prompt files
      const promptFilesResponse = await fetch('http://localhost:5000/api/workflow/prompt-files');
      if (promptFilesResponse.ok) {
        const files = await promptFilesResponse.json();
        setAvailablePromptFiles(files);
      }

      // Get prompts from current file
      if (config.promptFile !== 'default') {
        loadPromptsFromFile(config.promptFile);
      }
    } catch (error) {
      console.error('Failed to load workflow options:', error);
    }
  };

  const loadPromptsFromFile = async (filename) => {
    try {
      const response = await fetch(`http://localhost:5000/api/workflow/prompts/${filename}`);
      if (response.ok) {
        const prompts = await response.json();
        setAvailablePrompts(prompts);
      }
    } catch (error) {
      console.error('Failed to load prompts:', error);
    }
  };

  const handlePromptFileChange = (filename) => {
    setConfig(prev => ({ ...prev, promptFile: filename }));
    if (filename !== 'default') {
      loadPromptsFromFile(filename);
    }
  };

  const handleModelToggle = (model) => {
    setConfig(prev => {
      const newModels = prev.specificModels.includes(model)
        ? prev.specificModels.filter(m => m !== model)
        : [...prev.specificModels, model];
      return { ...prev, specificModels: newModels };
    });
  };

  const handlePromptToggle = (promptId) => {
    setConfig(prev => {
      const newPrompts = prev.specificPrompts.includes(promptId)
        ? prev.specificPrompts.filter(p => p !== promptId)
        : [...prev.specificPrompts, promptId];
      return { ...prev, specificPrompts: newPrompts };
    });
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    try {
      await onRunWorkflow(config);
      onClose();
    } catch (error) {
      console.error('Workflow execution failed:', error);
      alert('Failed to start workflow: ' + error.message);
    }
    setIsLoading(false);
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🚀 Configure New Workflow</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {/* Prompt File Selection */}
          <div className="config-section">
            <label className="config-label">Prompt File</label>
            <select 
              value={config.promptFile} 
              onChange={e => handlePromptFileChange(e.target.value)}
              className="config-select"
            >
              <option value="default">Default (prompts.json)</option>
              {availablePromptFiles.map(file => (
                <option key={file} value={file}>{file}</option>
              ))}
            </select>
          </div>

          {/* Model Selection */}
          <div className="config-section">
            <label className="config-label">Models</label>
            <div className="config-radio-group">
              <label className="config-radio">
                <input 
                  type="radio" 
                  name="models" 
                  checked={config.models === 'all'}
                  onChange={() => setConfig(prev => ({ ...prev, models: 'all' }))}
                />
                All Available Models
              </label>
              <label className="config-radio">
                <input 
                  type="radio" 
                  name="models" 
                  checked={config.models === 'specific'}
                  onChange={() => setConfig(prev => ({ ...prev, models: 'specific' }))}
                />
                Select Specific Models
              </label>
            </div>
            
            {config.models === 'specific' && (
              <div className="config-checkboxes">
                {availableModels.map(model => (
                  <label key={model} className="config-checkbox">
                    <input 
                      type="checkbox" 
                      checked={config.specificModels.includes(model)}
                      onChange={() => handleModelToggle(model)}
                    />
                    {model}
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Prompt Selection */}
          <div className="config-section">
            <label className="config-label">Prompts</label>
            <div className="config-radio-group">
              <label className="config-radio">
                <input 
                  type="radio" 
                  name="prompts" 
                  checked={config.prompts === 'all'}
                  onChange={() => setConfig(prev => ({ ...prev, prompts: 'all' }))}
                />
                All Prompts
              </label>
              <label className="config-radio">
                <input 
                  type="radio" 
                  name="prompts" 
                  checked={config.prompts === 'specific'}
                  onChange={() => setConfig(prev => ({ ...prev, prompts: 'specific' }))}
                />
                Select Specific Prompts
              </label>
            </div>
            
            {config.prompts === 'specific' && availablePrompts.length > 0 && (
              <div className="config-checkboxes">
                {availablePrompts.map(prompt => (
                  <label key={prompt.id} className="config-checkbox">
                    <input 
                      type="checkbox" 
                      checked={config.specificPrompts.includes(prompt.id)}
                      onChange={() => handlePromptToggle(prompt.id)}
                    />
                    {prompt.id} - {prompt.text?.substring(0, 50)}...
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Processing Options */}
          <div className="config-section">
            <label className="config-label">Processing Options</label>
            <div className="config-checkboxes">
              <label className="config-checkbox">
                <input 
                  type="checkbox" 
                  checked={config.removeBackground}
                  onChange={e => setConfig(prev => ({ ...prev, removeBackground: e.target.checked }))}
                />
                🎭 Remove Background
              </label>
              <label className="config-checkbox">
                <input 
                  type="checkbox" 
                  checked={config.createICO}
                  onChange={e => setConfig(prev => ({ ...prev, createICO: e.target.checked }))}
                />
                🔄 Create ICO Files
              </label>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="modal-button secondary" onClick={onClose} disabled={isLoading}>
            Cancel
          </button>
          <button 
            className="modal-button primary" 
            onClick={handleSubmit} 
            disabled={isLoading}
          >
            {isLoading ? '🔄 Starting...' : '▶️ Run Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
}