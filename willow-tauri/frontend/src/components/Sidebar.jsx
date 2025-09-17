import React from "react";
import "./Sidebar.css";

const Sidebar = ({ activeTab, setActiveTab, capabilities }) => {
  const tabs = [
    {
      id: "chat",
      label: "Chat",
      icon: "💬",
      description: "Chat with AI models",
      available: capabilities.core_llm !== false,
    },
    {
      id: "rag",
      label: "RAG",
      icon: "📚",
      description: "Document-augmented queries",
      available: capabilities.rag_simple || capabilities.rag_full,
    },
    {
      id: "willow-chat",
      label: "Willow Chat",
      icon: "🌿",
      description: "Direct chat with backend",
      available: true,
    },
    {
      id: "settings",
      label: "Settings",
      icon: "⚙️",
      description: "Configure Willow",
      available: true,
    },
    {
      id: "status",
      label: "Status",
      icon: "📊",
      description: "System information",
      available: true,
    },
  ];

  const handleTabClick = (tabId, available) => {
    if (available) {
      setActiveTab(tabId);
    }
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h3>Navigation</h3>
      </div>

      <ul className="tab-list">
        {tabs.map((tab) => (
          <li key={tab.id} className="tab-item">
            <button
              className={`tab-button ${activeTab === tab.id ? "active" : ""} ${
                !tab.available ? "disabled" : ""
              }`}
              onClick={() => handleTabClick(tab.id, tab.available)}
              disabled={!tab.available}
              title={
                tab.available
                  ? tab.description
                  : `${tab.description} (Not available)`
              }
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
              {!tab.available && (
                <span className="tab-disabled-indicator">⚠️</span>
              )}
            </button>
          </li>
        ))}
      </ul>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          <div className="info-item">
            <span className="info-label">Active:</span>
            <span className="info-value">
              {tabs.find((t) => t.id === activeTab)?.label || "Unknown"}
            </span>
          </div>
          <div className="info-item">
            <span className="info-label">Available:</span>
            <span className="info-value">
              {tabs.filter((t) => t.available).length}/{tabs.length}
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Sidebar;
