import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { thinkingPulse, panelSlideFade } from '../../variants/framerVariants';
import NavBar from '../../components/organisms/NavBar';
import ModelSwitcher from '../../components/organisms/ModelSwitcher';
import ChatMessage from '../../components/molecules/ChatMessage';
import { listModels } from '../../lib/api/models';

const MainWorkspace = () => {
  const [activeTab, setActiveTab] = useState('Chat');
  const [models, setModels] = useState([]);
  const [activeModelId, setActiveModelId] = useState('');
  const [chainedMode, setChainedMode] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: '1',
      author: 'ai',
      content: 'Hello! I\'m Willow AI. How can I assist you today?',
      timeISO: new Date().toISOString(),
      metadata: { model: 'GPT-4' }
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const fetchedModels = await listModels();
        setModels(fetchedModels);
        if (fetchedModels.length > 0) {
          setActiveModelId(fetchedModels[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
      }
    };

    fetchModels();
  }, []);

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  const handleSearch = (term) => {
    console.log('Search term:', term);
  };

  const handleModelSelect = (modelId) => {
    setActiveModelId(modelId);
  };

  const handleToggleChained = (enabled) => {
    setChainedMode(enabled);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      author: 'user',
      content: inputValue,
      timeISO: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsThinking(true);
    
    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        author: 'ai',
        content: `I received your message: "${inputValue}". This is a simulated response from the AI model.`,
        timeISO: new Date().toISOString(),
        metadata: { model: models.find(m => m.id === activeModelId)?.name || 'Unknown' }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setIsThinking(false);
    }, 1500);
  };

  return (
    <div className="flex flex-col h-screen bg-willow-bg">
      <NavBar 
        activeTab={activeTab} 
        onTabClick={handleTabClick} 
        onSearch={handleSearch} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Chat Header */}
        <div className="border-b border-willow-muted p-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-willow-text">Main Workspace</h1>
          <ModelSwitcher 
            models={models}
            activeModelId={activeModelId}
            chainedMode={chainedMode}
            onSelect={handleModelSelect}
            onToggleChained={handleToggleChained}
          />
        </div>
        
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto">
          {messages.map((message) => (
            <ChatMessage key={message.id} {...message} />
          ))}
          
          {isThinking && (
            <motion.div
              variants={thinkingPulse}
              initial="initial"
              animate="animate"
              className="py-4 px-4 bg-willow-card border-l-4 border-willow-accent"
            >
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 rounded-full bg-willow-accent flex items-center justify-center">
                  <span className="text-xs font-bold text-willow-text">AI</span>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-willow-text">Willow AI is thinking...</div>
                  <div className="mt-2 flex space-x-1">
                    <div className="w-2 h-2 bg-willow-accent rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-willow-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-willow-accent rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
        
        {/* Chat Input */}
        <motion.div
          variants={panelSlideFade}
          initial="initial"
          animate="animate"
          className="border-t border-willow-muted p-4"
        >
          <form onSubmit={handleSubmit} className="flex items-end space-x-2">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 bg-willow-card text-willow-text rounded-lg px-4 py-3 border border-willow-muted focus:outline-none focus:ring-1 focus:ring-willow-accent resize-none"
              rows="1"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isThinking}
              className="bg-willow-accent text-willow-text rounded-lg px-4 py-3 hover:bg-opacity-80 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </form>
          <div className="mt-2 text-xs text-willow-muted flex justify-between">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>{inputValue.length}/2000</span>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default MainWorkspace;