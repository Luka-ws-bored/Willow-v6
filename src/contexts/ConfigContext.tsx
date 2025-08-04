import React, { createContext, useContext, useState, useEffect } from 'react';
import { useQuery } from 'convex/react';
import { api } from '../../convex/_generated/api';

interface ConfigContextType {
  config: {
    LLM_MODE: string;
    MODEL_NAME: string;
    LOCAL_API_URL: string;
    RETRIEVAL_K: string;
  };
  isLoading: boolean;
}

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function ConfigProvider({ children }: { children: React.ReactNode }) {
  const [config, setConfig] = useState({
    LLM_MODE: 'local',
    MODEL_NAME: 'default',
    LOCAL_API_URL: 'http://localhost:8000',
    RETRIEVAL_K: '5',
  });
  const [isLoading, setIsLoading] = useState(true);

  // Simulate loading config from environment
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <ConfigContext.Provider value={{ config, isLoading }}>
      {children}
    </ConfigContext.Provider>
  );
}

export function useConfig() {
  const context = useContext(ConfigContext);
  if (context === undefined) {
    throw new Error('useConfig must be used within a ConfigProvider');
  }
  return context;
}
