import { useState } from 'react'
import MainWorkspace from './screens/MainWorkspace/MainWorkspace'
import PromptVault from './screens/PromptVault/PromptVault'
import RAGDashboard from './screens/RAGDashboard/RAGDashboard'

function App() {
  const [currentScreen, setCurrentScreen] = useState('main')

  const renderScreen = () => {
    switch (currentScreen) {
      case 'main':
        return <MainWorkspace />
      case 'promptVault':
        return <PromptVault />
      case 'rag':
        return <RAGDashboard />
      default:
        return <MainWorkspace />
    }
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="flex bg-willow-card border-b border-willow-muted">
        <button 
          onClick={() => setCurrentScreen('main')}
          className={`px-4 py-2 text-sm ${currentScreen === 'main' ? 'bg-willow-accent text-willow-text' : 'text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'}`}
        >
          Main Workspace
        </button>
        <button 
          onClick={() => setCurrentScreen('promptVault')}
          className={`px-4 py-2 text-sm ${currentScreen === 'promptVault' ? 'bg-willow-accent text-willow-text' : 'text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'}`}
        >
          Prompt Vault
        </button>
        <button 
          onClick={() => setCurrentScreen('rag')}
          className={`px-4 py-2 text-sm ${currentScreen === 'rag' ? 'bg-willow-accent text-willow-text' : 'text-willow-muted hover:bg-willow-accent hover:bg-opacity-20'}`}
        >
          RAG Dashboard
        </button>
      </div>
      <div className="flex-1 overflow-hidden">
        {renderScreen()}
      </div>
    </div>
  )
}

export default App
