import React, { useState, useEffect } from "react";
import { api } from "../utils/invokeBridge";
import "./StatusInterface.css";

const StatusInterface = ({ appState, refreshStatus, setIsLoading }) => {
  const [systemInfo, setSystemInfo] = useState({});
  const [performanceMetrics, setPerformanceMetrics] = useState({});
  const [lastRefresh, setLastRefresh] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);

  useEffect(() => {
    loadSystemInfo();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        handleRefresh();
      }, 10000); // Refresh every 10 seconds
      setRefreshInterval(interval);
    } else {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }

    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [autoRefresh]);

  const loadSystemInfo = async () => {
    try {
      const response = await api.getSystemInfo();
      if (response.success && response.data) {
        setSystemInfo(JSON.parse(response.data));
      }
    } catch (error) {
      console.error("Failed to load system info:", error);
    }
  };

  const loadPerformanceMetrics = async () => {
    try {
      const response = await api.getPerformanceMetrics();
      if (response.success && response.data) {
        setPerformanceMetrics(JSON.parse(response.data));
      }
    } catch (error) {
      console.error("Failed to load performance metrics:", error);
    }
  };

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        refreshStatus(),
        loadSystemInfo(),
        loadPerformanceMetrics(),
      ]);
      setLastRefresh(new Date());
    } catch (error) {
      console.error("Failed to refresh status:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const formatBytes = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (days > 0) {
      return `${days}d ${hours}h ${minutes}m`;
    } else if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else {
      return `${minutes}m`;
    }
  };

  const getStatusIcon = (isConnected) => {
    return isConnected ? "🟢" : "🔴";
  };

  const getStatusText = (isConnected) => {
    return isConnected ? "Connected" : "Disconnected";
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return "Never";
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(timestamp);
  };

  return (
    <div className="status-interface">
      <div className="status-header">
        <div className="status-title">
          <h2>📊 System Status</h2>
          <span className="status-subtitle">Willow system information</span>
        </div>

        <div className="status-controls">
          <div className="auto-refresh-toggle">
            <label htmlFor="auto-refresh">
              <input
                id="auto-refresh"
                type="checkbox"
                checked={autoRefresh}
                onChange={toggleAutoRefresh}
              />
              Auto-refresh (10s)
            </label>
          </div>

          <button
            className="refresh-button"
            onClick={handleRefresh}
            disabled={autoRefresh}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      <div className="status-content">
        <div className="status-grid">
          {/* Connection Status */}
          <div className="status-card connection-card">
            <h3>🔗 Connection Status</h3>
            <div className="status-main">
              <div className="connection-indicator">
                <span className="status-icon">
                  {getStatusIcon(appState.isConnected)}
                </span>
                <span
                  className={`status-text ${
                    appState.isConnected ? "connected" : "disconnected"
                  }`}
                >
                  {getStatusText(appState.isConnected)}
                </span>
              </div>
              {lastRefresh && (
                <div className="last-refresh">
                  Last refresh: {formatTimestamp(lastRefresh)}
                </div>
              )}
            </div>
          </div>

          {/* Capabilities Overview */}
          <div className="status-card capabilities-card">
            <h3>🎯 Capabilities</h3>
            <div className="capabilities-list">
              {Object.entries(appState.capabilities).map(([key, available]) => (
                <div key={key} className="capability-item">
                  <span
                    className={`capability-status ${
                      available ? "available" : "unavailable"
                    }`}
                  >
                    {available ? "✅" : "❌"}
                  </span>
                  <span className="capability-name">
                    {key
                      .replace(/_/g, " ")
                      .replace(/\b\w/g, (l) => l.toUpperCase())}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Models Information */}
          <div className="status-card models-card">
            <h3>🤖 Available Models</h3>
            <div className="models-info">
              <div className="models-count">
                <strong>{appState.models.length}</strong> models available
              </div>
              {appState.models.length > 0 && (
                <div className="models-list">
                  {appState.models.slice(0, 5).map((model, index) => (
                    <div key={index} className="model-item">
                      {model}
                    </div>
                  ))}
                  {appState.models.length > 5 && (
                    <div className="model-item more">
                      +{appState.models.length - 5} more...
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* System Information */}
          {Object.keys(systemInfo).length > 0 && (
            <div className="status-card system-card">
              <h3>💻 System Information</h3>
              <div className="system-metrics">
                {systemInfo.cpu_percent && (
                  <div className="metric-item">
                    <span className="metric-label">CPU Usage:</span>
                    <span className="metric-value">
                      {systemInfo.cpu_percent.toFixed(1)}%
                    </span>
                  </div>
                )}
                {systemInfo.memory && (
                  <div className="metric-item">
                    <span className="metric-label">Memory:</span>
                    <span className="metric-value">
                      {formatBytes(systemInfo.memory.used)} /{" "}
                      {formatBytes(systemInfo.memory.total)}
                    </span>
                  </div>
                )}
                {systemInfo.disk && (
                  <div className="metric-item">
                    <span className="metric-label">Disk:</span>
                    <span className="metric-value">
                      {formatBytes(systemInfo.disk.used)} /{" "}
                      {formatBytes(systemInfo.disk.total)}
                    </span>
                  </div>
                )}
                {systemInfo.uptime && (
                  <div className="metric-item">
                    <span className="metric-label">Uptime:</span>
                    <span className="metric-value">
                      {formatUptime(systemInfo.uptime)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Performance Metrics */}
          {Object.keys(performanceMetrics).length > 0 && (
            <div className="status-card performance-card">
              <h3>⚡ Performance Metrics</h3>
              <div className="performance-metrics">
                {performanceMetrics.cache_hit_rate && (
                  <div className="metric-item">
                    <span className="metric-label">Cache Hit Rate:</span>
                    <span className="metric-value">
                      {(performanceMetrics.cache_hit_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                )}
                {performanceMetrics.avg_response_time && (
                  <div className="metric-item">
                    <span className="metric-label">Avg Response Time:</span>
                    <span className="metric-value">
                      {performanceMetrics.avg_response_time.toFixed(3)}s
                    </span>
                  </div>
                )}
                {performanceMetrics.total_requests && (
                  <div className="metric-item">
                    <span className="metric-label">Total Requests:</span>
                    <span className="metric-value">
                      {performanceMetrics.total_requests}
                    </span>
                  </div>
                )}
                {performanceMetrics.error_rate && (
                  <div className="metric-item">
                    <span className="metric-label">Error Rate:</span>
                    <span className="metric-value">
                      {(performanceMetrics.error_rate * 100).toFixed(2)}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Version Information */}
          <div className="status-card version-card">
            <h3>📋 Version Information</h3>
            <div className="version-info">
              <div className="version-item">
                <span className="version-label">Willow:</span>
                <span className="version-value">v6.0.0</span>
              </div>
              <div className="version-item">
                <span className="version-label">Tauri:</span>
                <span className="version-value">v2.8.0</span>
              </div>
              <div className="version-item">
                <span className="version-label">React:</span>
                <span className="version-value">v19.1.1</span>
              </div>
              <div className="version-item">
                <span className="version-label">Build:</span>
                <span className="version-value">Desktop</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusInterface;
