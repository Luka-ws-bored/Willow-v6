import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { classNames } from '../../lib/utils';

const ChatMessage = ({ 
  id,
  author,
  avatarUrl,
  content,
  timeISO,
  metadata,
  collapsed = false
}) => {
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  const [copied, setCopied] = useState(false);
  
  const formatTime = (isoString) => {
    return new Date(isoString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getAuthorStyles = () => {
    switch (author) {
      case 'ai':
        return 'bg-willow-card border-l-4 border-willow-accent';
      case 'user':
        return 'bg-willow-bg';
      case 'system':
        return 'bg-willow-card border-l-4 border-yellow-500';
      default:
        return '';
    }
  };

  const getAvatar = () => {
    if (avatarUrl) {
      return <img src={avatarUrl} alt={`${author} avatar`} className="w-8 h-8 rounded-full" />;
    }
    
    switch (author) {
      case 'ai':
        return (
          <div className="w-8 h-8 rounded-full bg-willow-accent flex items-center justify-center">
            <span className="text-xs font-bold text-willow-text">AI</span>
          </div>
        );
      case 'user':
        return (
          <div className="w-8 h-8 rounded-full bg-willow-muted flex items-center justify-center">
            <span className="text-xs font-bold text-willow-text">U</span>
          </div>
        );
      case 'system':
        return (
          <div className="w-8 h-8 rounded-full bg-yellow-500 flex items-center justify-center">
            <span className="text-xs font-bold text-willow-text">S</span>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center">
            <span className="text-xs font-bold text-willow-text">?</span>
          </div>
        );
    }
  };

  return (
    <div 
      className={classNames(
        'py-4 px-4 transition-colors',
        getAuthorStyles()
      )}
      role="log"
      aria-label={`${author} message at ${formatTime(timeISO)}`}
    >
      <div className="flex items-start space-x-3">
        {getAvatar()}
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <div className="text-sm font-medium text-willow-text">
              {author === 'ai' ? 'Willow AI' : author === 'user' ? 'You' : 'System'}
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-willow-muted">{formatTime(timeISO)}</span>
              <button 
                onClick={copyToClipboard}
                className="text-willow-muted hover:text-willow-text transition-colors"
                aria-label="Copy message"
              >
                {copied ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-green-500" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                    <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                  </svg>
                )}
              </button>
              <button 
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="text-willow-muted hover:text-willow-text transition-colors"
                aria-label={isCollapsed ? "Expand message" : "Collapse message"}
              >
                {isCollapsed ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            </div>
          </div>
          
          {!isCollapsed && (
            <div className="mt-2">
              <ReactMarkdown className="text-willow-text text-sm prose prose-invert max-w-none">
                {content}
              </ReactMarkdown>
              
              {metadata && (
                <div className="mt-2 flex items-center space-x-2 text-xs text-willow-muted">
                  {metadata.model && <span>Model: {metadata.model}</span>}
                  {metadata.tokensUsed && <span>Tokens: {metadata.tokensUsed}</span>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;