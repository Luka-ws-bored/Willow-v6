import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { panelSlideFade } from '../../variants/framerVariants';
import NavBar from '../../components/organisms/NavBar';

const PromptVault = () => {
  const [activeTab, setActiveTab] = useState('Prompt Vault');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  // Mock data for prompts
  const prompts = [
    {
      id: '1',
      title: 'Creative Story Generator',
      category: 'Creative',
      prompt: 'Write a short story about {topic} in the style of {author}. The story should include {character} and take place in {setting}.',
      tags: ['story', 'creative', 'fiction'],
      createdAt: '2023-05-15',
      updatedAt: '2023-05-20'
    },
    {
      id: '2',
      title: 'Code Explanation',
      category: 'Development',
      prompt: 'Explain the following code in simple terms:\n\n{code}\n\nInclude:\n1. What it does\n2. How it works\n3. Potential improvements',
      tags: ['code', 'explanation', 'learning'],
      createdAt: '2023-05-10',
      updatedAt: '2023-05-18'
    },
    {
      id: '3',
      title: 'Business Email Template',
      category: 'Business',
      prompt: 'Write a professional email to {recipient} regarding {topic}. The tone should be {tone} and include a clear call to action.',
      tags: ['email', 'business', 'communication'],
      createdAt: '2023-05-05',
      updatedAt: '2023-05-12'
    }
  ];
  
  const categories = ['All', 'Creative', 'Development', 'Business', 'Education', 'Other'];
  
  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          prompt.prompt.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || prompt.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  return (
    <div className="flex flex-col h-screen bg-willow-bg">
      <NavBar 
        activeTab={activeTab} 
        onTabClick={handleTabClick} 
        onSearch={handleSearch} 
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="border-b border-willow-muted p-4">
          <h1 className="text-xl font-bold text-willow-text mb-4">Prompt Vault</h1>
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search prompts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-willow-card text-willow-text rounded-lg px-4 py-2 border border-willow-muted focus:outline-none focus:ring-1 focus:ring-willow-accent"
              />
            </div>
            
            <div className="flex space-x-2 overflow-x-auto pb-2 md:pb-0">
              {categories.map(category => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1 rounded-full text-sm whitespace-nowrap ${
                    selectedCategory === category
                      ? 'bg-willow-accent text-willow-text'
                      : 'bg-willow-card text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>
        
        {/* Prompt List */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPrompts.map(prompt => (
              <motion.div
                key={prompt.id}
                variants={panelSlideFade}
                initial="initial"
                animate="animate"
                className="bg-willow-card rounded-lg border border-willow-muted overflow-hidden hover:border-willow-accent transition-colors"
              >
                <div className="p-4">
                  <div className="flex justify-between items-start">
                    <h3 className="font-bold text-willow-text">{prompt.title}</h3>
                    <span className="text-xs bg-willow-accent bg-opacity-20 text-willow-accent px-2 py-1 rounded">
                      {prompt.category}
                    </span>
                  </div>
                  
                  <p className="mt-2 text-sm text-willow-muted line-clamp-3">
                    {prompt.prompt}
                  </p>
                  
                  <div className="mt-3 flex flex-wrap gap-1">
                    {prompt.tags.map(tag => (
                      <span key={tag} className="text-xs bg-willow-bg text-willow-muted px-2 py-1 rounded">
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="mt-4 flex justify-between text-xs text-willow-muted">
                    <span>Created: {prompt.createdAt}</span>
                    <span>Updated: {prompt.updatedAt}</span>
                  </div>
                </div>
                
                <div className="bg-willow-bg px-4 py-2 flex justify-end space-x-2">
                  <button className="text-willow-muted hover:text-willow-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button className="text-willow-muted hover:text-willow-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                  <button className="text-willow-muted hover:text-willow-text transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
          
          {filteredPrompts.length === 0 && (
            <div className="text-center py-12">
              <div className="text-willow-muted">No prompts found</div>
              <button className="mt-4 text-willow-accent hover:text-willow-text transition-colors">
                Create your first prompt
              </button>
            </div>
          )}
        </div>
        
        {/* Floating Action Button */}
        <button className="fixed bottom-6 right-6 bg-willow-accent text-willow-text rounded-full p-3 shadow-lg hover:bg-opacity-80 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default PromptVault;