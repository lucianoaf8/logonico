// components/Gallery/SelectionActions.js
import React, { useState } from 'react';
import styled from 'styled-components';
import ActionButton from '../common/ActionButton';
import { InlineSpinner } from '../common/LoadingSpinner';

const ActionsContainer = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
`;

const ActionGroup = styled.div`
  display: flex;
  gap: 4px;
  flex: 1;
  min-width: 120px;
`;

const BulkActionButton = styled(ActionButton)`
  flex: 1;
  font-size: 12px;
  padding: 8px 12px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ProgressIndicator = styled.div`
  margin-top: 8px;
  padding: 8px 12px;
  background: var(--bg-primary);
  border-radius: 6px;
  border: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: var(--text-secondary);
`;

const SelectionActions = ({
  selectedImages = [],
  onRemoveBackground,
  onConvertToICO,
  onDownloadSelected,
  onDeleteSelected,
  onClearSelection,
  isProcessing = false,
  processingStatus = null,
  className
}) => {
  const [activeOperation, setActiveOperation] = useState(null);
  
  const hasSelection = selectedImages.length > 0;
  const isDisabled = isProcessing || !hasSelection;

  const handleAction = async (action, operation) => {
    if (isDisabled) return;
    
    setActiveOperation(operation);
    try {
      await action(selectedImages);
    } finally {
      setActiveOperation(null);
    }
  };

  const getButtonState = (operation) => ({
    disabled: isDisabled,
    loading: activeOperation === operation,
    icon: activeOperation === operation ? <InlineSpinner /> : undefined
  });

  return (
    <div className={className}>
      <ActionsContainer>
        <ActionGroup>
          <BulkActionButton
            variant="primary"
            onClick={() => handleAction(onRemoveBackground, 'removeBg')}
            {...getButtonState('removeBg')}
            title={hasSelection ? `Remove background from ${selectedImages.length} images` : 'Select images first'}
          >
            🎭 Remove BG
          </BulkActionButton>
          
          <BulkActionButton
            variant="secondary"
            onClick={() => handleAction(onConvertToICO, 'convertIco')}
            {...getButtonState('convertIco')}
            title={hasSelection ? `Convert ${selectedImages.length} images to ICO` : 'Select images first'}
          >
            🔄 To ICO
          </BulkActionButton>
        </ActionGroup>

        <ActionGroup>
          <BulkActionButton
            variant="success"
            onClick={() => handleAction(onDownloadSelected, 'download')}
            {...getButtonState('download')}
            title={hasSelection ? `Download ${selectedImages.length} selected images` : 'Select images first'}
          >
            💾 Download
          </BulkActionButton>
          
          <BulkActionButton
            variant="danger"
            onClick={() => handleAction(onDeleteSelected, 'delete')}
            {...getButtonState('delete')}
            title={hasSelection ? `Delete ${selectedImages.length} selected images` : 'Select images first'}
          >
            🗑️ Delete
          </BulkActionButton>
        </ActionGroup>
      </ActionsContainer>

      {hasSelection && !isProcessing && (
        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <ActionButton
            variant="ghost"
            size="small"
            onClick={onClearSelection}
          >
            Clear Selection ({selectedImages.length})
          </ActionButton>
        </div>
      )}

      {processingStatus && (
        <ProgressIndicator>
          {processingStatus.message}
          {processingStatus.progress && (
            <div style={{ marginTop: '4px' }}>
              Progress: {processingStatus.current}/{processingStatus.total} 
              ({Math.round(processingStatus.percentage)}%)
            </div>
          )}
        </ProgressIndicator>
      )}
    </div>
  );
};

// Quick action buttons for common operations
export const QuickActions = ({ 
  selectedImages, 
  onSelectAll, 
  onDeselectAll, 
  totalImages,
  className 
}) => (
  <div className={className} style={{ display: 'flex', gap: '4px', marginBottom: '8px' }}>
    <ActionButton
      variant="ghost"
      size="small"
      onClick={onSelectAll}
      disabled={selectedImages.length === totalImages}
    >
      Select All ({totalImages})
    </ActionButton>
    
    <ActionButton
      variant="ghost"
      size="small"
      onClick={onDeselectAll}
      disabled={selectedImages.length === 0}
    >
      Clear ({selectedImages.length})
    </ActionButton>
  </div>
);

// Batch operation status
export const BatchOperationStatus = ({ 
  operation, 
  progress, 
  onCancel 
}) => {
  if (!operation) return null;

  return (
    <ProgressIndicator>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: '500', marginBottom: '2px' }}>
            {operation.title || 'Processing...'}
          </div>
          <div style={{ fontSize: '11px' }}>
            {progress.current}/{progress.total} completed
          </div>
        </div>
        
        {onCancel && (
          <ActionButton
            variant="danger"
            size="small"
            onClick={onCancel}
          >
            Cancel
          </ActionButton>
        )}
      </div>
      
      <div style={{ 
        width: '100%', 
        height: '4px', 
        background: 'var(--bg-secondary)', 
        borderRadius: '2px',
        marginTop: '8px',
        overflow: 'hidden'
      }}>
        <div style={{
          width: `${progress.percentage}%`,
          height: '100%',
          background: 'var(--accent-blue)',
          transition: 'width 0.2s ease'
        }} />
      </div>
    </ProgressIndicator>
  );
};

export default SelectionActions;