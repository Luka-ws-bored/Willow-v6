import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { panelSlideFade } from '../../variants/framerVariants';
import NavBar from '../../components/organisms/NavBar';
import { listIndexes, ingestFile, queryRAG } from '../../lib/api/rag';

const RAGDashboard = () => {
  const [activeTab, setActiveTab] = useState('RAG');
  const [indexes, setIndexes] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [query, setQuery] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [isQuerying, setIsQuerying] = useState(false);

  useEffect(() => {
    const fetchIndexes = async () => {
      try {
        const fetchedIndexes = await listIndexes();
        setIndexes(fetchedIndexes);
      } catch (error) {
        console.error('Failed to fetch indexes:', error);
      }
    };

    fetchIndexes();
  }, []);

  const handleTabClick = (tab) => {
    setActiveTab(tab);
  };

  const handleSearch = (term) => {
    console.log('Search term:', term);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    
    try {
      // Simulate file upload
      await new Promise(resolve => setTimeout(resolve, 1500));
      const result = await ingestFile(selectedFile);
      console.log('File ingested:', result);
      
      // Refresh indexes
      const fetchedIndexes = await listIndexes();
      setIndexes(fetchedIndexes);
      
      setSelectedFile(null);
    } catch (error) {
      console.error('Failed to ingest file:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const handleQuery = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setIsQuerying(true);
    
    try {
      // Simulate query
      await new Promise(resolve => setTimeout(resolve, 1000));
      const results = await queryRAG(query);
      setQueryResults(results);
    } catch (error) {
      console.error('Failed to query RAG:', error);
    } finally {
      setIsQuerying(false);
    }
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
          <h1 className="text-xl font-bold text-willow-text">RAG Dashboard</h1>
        </div>
        
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* Left Panel - Indexes and Upload */}
          <div className="w-full md:w-1/3 border-r border-willow-muted flex flex-col">
            <div className="p-4 border-b border-willow-muted">
              <h2 className="font-bold text-willow-text mb-3">Document Indexes</h2>
              
              <div className="space-y-3">
                {indexes.map(index => (
                  <motion.div
                    key={index.id}
                    variants={panelSlideFade}
                    initial="initial"
                    animate="animate"
                    className="bg-willow-card rounded-lg p-3 border border-willow-muted"
                  >
                    <div className="flex justify-between">
                      <h3 className="font-medium text-willow-text">{index.name}</h3>
                      <span className="text-xs bg-willow-accent bg-opacity-20 text-willow-accent px-2 py-1 rounded">
                        {index.documentCount} docs
                      </span>
                    </div>
                    <div className="mt-2 text-xs text-willow-muted">
                      Last updated: {index.lastUpdated}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
            
            <div className="p-4 flex-1">
              <h2 className="font-bold text-willow-text mb-3">Upload Documents</h2>
              
              <div className="bg-willow-card rounded-lg border-2 border-dashed border-willow-muted p-6 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-willow-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                
                <p className="mt-2 text-willow-text">
                  {selectedFile ? selectedFile.name : 'Drag and drop files here'}
                </p>
                
                <p className="mt-1 text-sm text-willow-muted">
                  Supported formats: PDF, TXT, DOCX
                </p>
                
                <div className="mt-4">
                  <label className="cursor-pointer">
                    <span className="bg-willow-accent text-willow-text rounded-md px-4 py-2 text-sm hover:bg-opacity-80 transition-colors">
                      Browse Files
                    </span>
                    <input 
                      type="file" 
                      className="hidden" 
                      onChange={handleFileChange}
                      accept=".pdf,.txt,.docx"
                    />
                  </label>
                  
                  {selectedFile && (
                    <button
                      onClick={handleUpload}
                      disabled={isUploading}
                      className="ml-2 bg-willow-card border border-willow-muted text-willow-text rounded-md px-4 py-2 text-sm hover:bg-willow-accent hover:bg-opacity-20 disabled:opacity-50 transition-colors"
                    >
                      {isUploading ? 'Uploading...' : 'Upload'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Right Panel - Query Interface */}
          <div className="w-full md:w-2/3 flex flex-col">
            <div className="p-4 border-b border-willow-muted">
              <h2 className="font-bold text-willow-text mb-3">Query Documents</h2>
              
              <form onSubmit={handleQuery}>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about your documents..."
                    className="flex-1 bg-willow-card text-willow-text rounded-lg px-4 py-2 border border-willow-muted focus:outline-none focus:ring-1 focus:ring-willow-accent"
                  />
                  <button
                    type="submit"
                    disabled={!query.trim() || isQuerying}
                    className="bg-willow-accent text-willow-text rounded-lg px-4 py-2 hover:bg-opacity-80 disabled:opacity-50 transition-colors"
                  >
                    {isQuerying ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </form>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4">
              {queryResults ? (
                <div className="space-y-4">
                  <div className="bg-willow-card rounded-lg p-4 border border-willow-muted">
                    <h3 className="font-bold text-willow-text mb-2">Response</h3>
                    <p className="text-willow-text">{queryResults.response}</p>
                  </div>
                  
                  <div>
                    <h3 className="font-bold text-willow-text mb-2">Retrieved Documents</h3>
                    <div className="space-y-3">
                      {queryResults.results.map((result, index) => (
                        <motion.div
                          key={result.id}
                          variants={panelSlideFade}
                          initial="initial"
                          animate="animate"
                          transition={{ delay: index * 0.1 }}
                          className="bg-willow-card rounded-lg p-4 border border-willow-muted"
                        >
                          <div className="flex justify-between">
                            <h4 className="font-medium text-willow-text">{result.source}</h4>
                            <span className="text-xs bg-willow-accent bg-opacity-20 text-willow-accent px-2 py-1 rounded">
                              {Math.round(result.score * 100)}% relevant
                            </span>
                          </div>
                          <p className="mt-2 text-willow-text">{result.content}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-willow-muted">
                    {query ? 'No results found' : 'Enter a query to search your documents'}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RAGDashboard;