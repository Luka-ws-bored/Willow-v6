import React, { useState } from 'react';

export interface MCP {
  id: string;
  name: string;
  description: string;
  category: 'analysis' | 'generation' | 'processing';
}

const AVAILABLE_MCPS: MCP[] = [
  {
    id: 'summarization',
    name: 'Document Summarization',
    description: 'Summarize long documents into key points',
    category: 'analysis'
  },
  {
    id: 'sql-analysis',
    name: 'SQL Analysis',
    description: 'Analyze and generate SQL queries from natural language',
    category: 'analysis'
  },
  {
    id: 'style-editing',
    name: 'Style Editing',
    description: 'Improve writing style and tone',
    category: 'processing'
  },
  {
    id: 'code-review',
    name: 'Code Review',
    description: 'Review code for best practices and bugs',
    category: 'analysis'
  },
  {
    id: 'creative-writing',
    name: 'Creative Writing',
    description: 'Generate creative content and stories',
    category: 'generation'
  }
];

interface MCPSelectorProps {
  selectedMCP: MCP | null;
  onMCPSelect: (mcp: MCP | null) => void;
}

export function MCPSelector({ selectedMCP, onMCPSelect }: MCPSelectorProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'analysis': return 'bg-blue-100 text-blue-800';
      case 'generation': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-purple-100 text-purple-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Model Context Protocols (MCP)</h3>
          {selectedMCP && (
            <p className="text-sm text-gray-600 mt-1">
              Selected: {selectedMCP.name}
            </p>
          )}
        </div>
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
        <div className="px-4 pb-4 border-t bg-gray-50">
          <div className="pt-4 space-y-2">
            <button
              onClick={() => onMCPSelect(null)}
              className={`w-full text-left p-3 rounded-lg border transition-colors ${
                !selectedMCP 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-gray-200 bg-white hover:bg-gray-50'
              }`}
            >
              <div className="font-medium text-gray-800">No MCP (Default)</div>
              <div className="text-sm text-gray-600">Use standard LLM processing</div>
            </button>
            
            {AVAILABLE_MCPS.map((mcp) => (
              <button
                key={mcp.id}
                onClick={() => onMCPSelect(mcp)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  selectedMCP?.id === mcp.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="font-medium text-gray-800">{mcp.name}</div>
                  <span className={`px-2 py-1 text-xs rounded-full ${getCategoryColor(mcp.category)}`}>
                    {mcp.category}
                  </span>
                </div>
                <div className="text-sm text-gray-600">{mcp.description}</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
