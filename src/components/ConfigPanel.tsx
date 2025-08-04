import React, { useState } from 'react';
import { useConfig } from '../contexts/ConfigContext';

export function ConfigPanel() {
  const { config, isLoading } = useConfig();
  const [isExpanded, setIsExpanded] = useState(false);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <h3 className="text-lg font-semibold text-gray-800">Environment Configuration</h3>
        <svg
          className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3 border-t bg-gray-50">
          <div className="grid grid-cols-2 gap-4 pt-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">LLM Mode</label>
              <div className="px-3 py-2 bg-white border rounded text-sm text-gray-600">
                {config.LLM_MODE}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Model Name</label>
              <div className="px-3 py-2 bg-white border rounded text-sm text-gray-600">
                {config.MODEL_NAME}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Local API URL</label>
              <div className="px-3 py-2 bg-white border rounded text-sm text-gray-600">
                {config.LOCAL_API_URL}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Retrieval K</label>
              <div className="px-3 py-2 bg-white border rounded text-sm text-gray-600">
                {config.RETRIEVAL_K}
              </div>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-3">
            These values are read from environment variables. Update them in your deployment settings.
          </p>
        </div>
      )}
    </div>
  );
}
