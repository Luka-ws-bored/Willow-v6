import React, { useState } from 'react';
import { classNames } from '../../lib/utils';

const ModelSwitcher = ({ 
  models, 
  activeModelId, 
  chainedMode, 
  onSelect, 
  onToggleChained 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const activeModel = models.find(model => model.id === activeModelId);
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'local': return 'bg-green-500';
      case 'remote': return 'bg-blue-500';
      case 'down': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="relative">
      <div className="flex items-center space-x-2">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-2 bg-willow-card border border-willow-muted rounded-md px-3 py-2 text-sm hover:bg-willow-accent hover:bg-opacity-20 transition-colors"
        >
          <span className="text-willow-text">{activeModel?.name || 'Select Model'}</span>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-willow-muted" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
        
        <button
          onClick={() => onToggleChained(!chainedMode)}
          className={classNames(
            'flex items-center space-x-1 rounded-md px-2 py-1 text-xs',
            chainedMode 
              ? 'bg-willow-accent text-willow-text' 
              : 'bg-willow-card border border-willow-muted text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'
          )}
        >
          <span>Chained</span>
        </button>
      </div>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-64 bg-willow-card border border-willow-muted rounded-md shadow-lg">
          <div className="py-1">
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  onSelect(model.id);
                  setIsOpen(false);
                }}
                className={classNames(
                  'flex items-center justify-between w-full px-4 py-2 text-sm text-left',
                  activeModelId === model.id 
                    ? 'bg-willow-accent bg-opacity-20 text-willow-text' 
                    : 'text-willow-text hover:bg-willow-accent hover:bg-opacity-10'
                )}
              >
                <div className="flex items-center space-x-2">
                  <div className={`h-2 w-2 rounded-full ${getStatusColor(model.status)}`}></div>
                  <span>{model.name}</span>
                </div>
                <div className="flex items-center space-x-2 text-willow-muted text-xs">
                  <span>{model.tps} tps</span>
                  <span>{model.context} ctx</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSwitcher;