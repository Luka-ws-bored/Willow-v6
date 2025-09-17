import React from "react";
import "./Header.css";

const Header = ({ appState }) => {
  const { isConnected, capabilities } = appState;

  const getConnectionStatus = () => {
    if (isConnected) {
      return {
        status: "Connected",
        className: "status-connected",
        icon: "🟢",
      };
    }
    return {
      status: "Disconnected",
      className: "status-disconnected",
      icon: "🔴",
    };
  };

  const connectionInfo = getConnectionStatus();

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="app-logo">
          <span className="logo-icon">🌲</span>
          <h1 className="app-title">Willow v6</h1>
        </div>
        <div className="app-subtitle">AI Automation Framework</div>
      </div>

      <div className="header-center">
        <div className="capability-indicators">
          {capabilities.core_llm && (
            <span className="capability-badge llm" title="LLM Support">
              🤖 LLM
            </span>
          )}
          {capabilities.rag_simple && (
            <span className="capability-badge rag" title="RAG Available">
              📚 RAG
            </span>
          )}
          {capabilities.vector_db && (
            <span className="capability-badge vector" title="Vector Database">
              🗄️ Vector
            </span>
          )}
          {capabilities.async_support && (
            <span className="capability-badge async" title="Async Support">
              ⚡ Async
            </span>
          )}
        </div>
      </div>

      <div className="header-right">
        <div className={`connection-status ${connectionInfo.className}`}>
          <span className="status-icon">{connectionInfo.icon}</span>
          <span className="status-text">{connectionInfo.status}</span>
        </div>
      </div>
    </header>
  );
};

export default Header;
