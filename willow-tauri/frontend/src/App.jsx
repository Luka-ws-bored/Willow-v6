import React, { useState, useEffect } from "react";
import { api } from "./utils/invokeBridge";
import "./App.css";
import ChatInterface from "./components/ChatInterface";
import RAGInterface from "./components/RAGInterface";
import SettingsInterface from "./components/SettingsInterface";
import StatusInterface from "./components/StatusInterface";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import LoadingOverlay from "./components/LoadingOverlay";
import WillowChat from "./components/WillowChat";

function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [isLoading, setIsLoading] = useState(false);
  const [appState, setAppState] = useState({
    isConnected: false,
    capabilities: {},
    models: [],
    settings: {
      defaultModel: "",
      defaultMaxTokens: 1000,
      defaultTopK: 3,
      theme: "dark",
    },
  });

  // Initialize app on mount
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    setIsLoading(true);
    try {
      await refreshStatus();
      loadSettings();
    } catch (error) {
      console.error("Failed to initialize app:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshStatus = async () => {
    try {
      const response = await api.getStatus();

      if (response.success && response.data) {
        const data = JSON.parse(response.data);
        setAppState((prev) => ({
          ...prev,
          isConnected: true,
          capabilities: data.capabilities || {},
          models: data.models || [],
        }));
      } else {
        setAppState((prev) => ({
          ...prev,
          isConnected: false,
        }));
      }
    } catch (error) {
      console.error("Status check failed:", error);
      setAppState((prev) => ({
        ...prev,
        isConnected: false,
      }));
    }
  };

  const loadSettings = () => {
    const saved = localStorage.getItem("willowSettings");
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        setAppState((prev) => ({
          ...prev,
          settings: { ...prev.settings, ...settings },
        }));
        // Apply theme
        document.documentElement.setAttribute(
          "data-theme",
          settings.theme || "dark"
        );
      } catch (error) {
        console.error("Failed to load settings:", error);
      }
    }
  };

  const saveSettings = (newSettings) => {
    const updatedSettings = { ...appState.settings, ...newSettings };
    localStorage.setItem("willowSettings", JSON.stringify(updatedSettings));
    setAppState((prev) => ({
      ...prev,
      settings: updatedSettings,
    }));

    // Apply theme immediately
    if (newSettings.theme) {
      document.documentElement.setAttribute("data-theme", newSettings.theme);
    }
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case "chat":
        return (
          <ChatInterface appState={appState} setIsLoading={setIsLoading} />
        );
      case "rag":
        return <RAGInterface appState={appState} setIsLoading={setIsLoading} />;
      case "willow-chat":
        return <WillowChat />;
      case "settings":
        return (
          <SettingsInterface appState={appState} saveSettings={saveSettings} />
        );
      case "status":
        return (
          <StatusInterface
            appState={appState}
            refreshStatus={refreshStatus}
            setIsLoading={setIsLoading}
          />
        );
      default:
        return <div>Tab not found</div>;
    }
  };

  return (
    <div className="app-container" data-theme={appState.settings.theme}>
      <Header appState={appState} />

      <main className="main-content">
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          capabilities={appState.capabilities}
        />

        <section className="content-area">{renderActiveTab()}</section>
      </main>

      {isLoading && <LoadingOverlay />}
    </div>
  );
}

export default App;
