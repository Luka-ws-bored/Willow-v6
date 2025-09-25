import React, { useState } from 'react';
import { classNames } from '../../lib/utils';

const NavBar = ({ activeTab, onTabClick, onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const tabs = [
    { id: 'Chat', label: 'Chat' },
    { id: 'Playground', label: 'Playground' },
    { id: 'Prompt Vault', label: 'Prompt Vault' },
    { id: 'RAG', label: 'RAG' },
    { id: 'Agents', label: 'Agents' },
    { id: 'Docs', label: 'Docs' },
    { id: 'Settings', label: 'Settings' }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    onSearch(searchTerm);
  };

  return (
    <nav className="bg-willow-card border-b border-willow-muted p-4 flex items-center justify-between">
      <div className="flex space-x-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={classNames(
              'px-3 py-2 rounded-md text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-willow-accent text-willow-text'
                : 'text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'
            )}
            onClick={() => onTabClick(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      
      <form onSubmit={handleSearch} className="flex items-center">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search..."
          className="bg-willow-bg text-willow-text rounded-md px-3 py-1 text-sm border border-willow-muted focus:outline-none focus:ring-1 focus:ring-willow-accent"
        />
        <button
          type="submit"
          className="ml-2 bg-willow-accent text-willow-text rounded-md px-3 py-1 text-sm hover:bg-opacity-80 transition-colors"
        >
          Search
        </button>
      </form>
      
      <div className="flex items-center space-x-2">
        <button className="text-willow-muted hover:text-willow-text transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
          </svg>
        </button>
        <button className="text-willow-muted hover:text-willow-text transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </nav>
  );
};

export default NavBar;