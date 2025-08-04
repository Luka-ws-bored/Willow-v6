import React, { useState } from 'react';
import { useMutation, useQuery } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { toast } from 'sonner';

interface CrewTask {
  id: string;
  name: string;
  description: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  result?: string;
  error?: string;
}

const AVAILABLE_CREWS = [
  {
    id: 'document-analysis',
    name: 'Document Analysis Crew',
    description: 'Analyze uploaded documents for insights and summaries',
    agents: ['Researcher', 'Analyst', 'Summarizer']
  },
  {
    id: 'content-generation',
    name: 'Content Generation Crew',
    description: 'Generate content based on user requirements',
    agents: ['Writer', 'Editor', 'Reviewer']
  },
  {
    id: 'data-processing',
    name: 'Data Processing Crew',
    description: 'Process and transform data using multiple agents',
    agents: ['Data Engineer', 'Validator', 'Formatter']
  }
];

export function CrewAIPanel() {
  const [selectedCrew, setSelectedCrew] = useState<string | null>(null);
  const [taskInput, setTaskInput] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  const activeTasks = useQuery(api.crew.getActiveTasks) || [];
  const launchCrewTask = useMutation(api.crew.launchTask);

  const handleLaunchTask = async () => {
    if (!selectedCrew || !taskInput.trim()) {
      toast.error('Please select a crew and provide task description');
      return;
    }

    try {
      await launchCrewTask({
        crewId: selectedCrew,
        taskDescription: taskInput.trim(),
      });
      
      toast.success('Crew task launched successfully');
      setTaskInput('');
    } catch (error) {
      console.error('Launch task error:', error);
      toast.error('Failed to launch crew task');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'failed': return 'bg-red-100 text-red-800';
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
          <h3 className="text-lg font-semibold text-gray-800">CrewAI Orchestration</h3>
          <p className="text-sm text-gray-600 mt-1">
            {activeTasks.length > 0 ? `${activeTasks.length} active task(s)` : 'No active tasks'}
          </p>
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
          <div className="pt-4 space-y-4">
            {/* Crew Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Crew</label>
              <div className="space-y-2">
                {AVAILABLE_CREWS.map((crew) => (
                  <button
                    key={crew.id}
                    onClick={() => setSelectedCrew(crew.id)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedCrew === crew.id 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 bg-white hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-gray-800">{crew.name}</div>
                    <div className="text-sm text-gray-600 mb-1">{crew.description}</div>
                    <div className="text-xs text-gray-500">
                      Agents: {crew.agents.join(', ')}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Task Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Task Description</label>
              <textarea
                value={taskInput}
                onChange={(e) => setTaskInput(e.target.value)}
                placeholder="Describe the task you want the crew to perform..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
                rows={3}
              />
            </div>

            {/* Launch Button */}
            <button
              onClick={handleLaunchTask}
              disabled={!selectedCrew || !taskInput.trim()}
              className="w-full px-4 py-2 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Launch Crew Task
            </button>

            {/* Active Tasks */}
            {activeTasks.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">Active Tasks</h4>
                <div className="space-y-2">
                  {activeTasks.map((task) => (
                    <div key={task._id} className="border rounded-lg p-3 bg-white">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-gray-800">{task.crewId}</div>
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(task.status)}`}>
                          {task.status}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600 mb-2">{task.taskDescription}</div>
                      {task.result && (
                        <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
                          <strong>Result:</strong> {task.result}
                        </div>
                      )}
                      {task.error && (
                        <div className="text-sm text-red-700 bg-red-50 p-2 rounded">
                          <strong>Error:</strong> {task.error}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
