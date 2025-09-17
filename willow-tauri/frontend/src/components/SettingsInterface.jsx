import React, { useState, useEffect } from "react";
import "./SettingsInterface.css";

const SettingsInterface = ({ appState, saveSettings }) => {
  const [formData, setFormData] = useState({
    defaultModel: "",
    defaultMaxTokens: 1000,
    defaultTopK: 3,
    theme: "dark",
    autoSave: true,
    enableNotifications: true,
    enableTelemetry: false,
    maxCacheSize: 100,
    requestTimeout: 30,
  });

  const [unsavedChanges, setUnsavedChanges] = useState(false);

  useEffect(() => {
    // Initialize form with current settings
    setFormData((prev) => ({
      ...prev,
      ...appState.settings,
    }));
  }, [appState.settings]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === "checkbox" ? checked : value;

    setFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }));
    setUnsavedChanges(true);
  };

  const handleSave = () => {
    saveSettings(formData);
    setUnsavedChanges(false);
  };

  const handleReset = () => {
    setFormData({
      ...appState.settings,
    });
    setUnsavedChanges(false);
  };

  const handleDefaults = () => {
    setFormData({
      defaultModel: appState.models[0] || "",
      defaultMaxTokens: 1000,
      defaultTopK: 3,
      theme: "dark",
      autoSave: true,
      enableNotifications: true,
      enableTelemetry: false,
      maxCacheSize: 100,
      requestTimeout: 30,
    });
    setUnsavedChanges(true);
  };

  const exportSettings = () => {
    const dataStr = JSON.stringify(formData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "willow-settings.json";
    link.click();
    URL.revokeObjectURL(url);
  };

  const importSettings = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const imported = JSON.parse(event.target.result);
        setFormData((prev) => ({
          ...prev,
          ...imported,
        }));
        setUnsavedChanges(true);
      } catch (error) {
        alert("Failed to import settings: Invalid JSON file");
      }
    };
    reader.readAsText(file);
    e.target.value = ""; // Reset file input
  };

  return (
    <div className="settings-interface">
      <div className="settings-header">
        <div className="settings-title">
          <h2>⚙️ Settings</h2>
          <span className="settings-subtitle">
            Configure Willow preferences
          </span>
        </div>

        <div className="settings-actions">
          {unsavedChanges && (
            <span className="unsaved-indicator">● Unsaved changes</span>
          )}
          <button
            type="button"
            className="reset-button"
            onClick={handleReset}
            disabled={!unsavedChanges}
          >
            Reset
          </button>
          <button
            type="button"
            className="save-button"
            onClick={handleSave}
            disabled={!unsavedChanges}
          >
            Save Changes
          </button>
        </div>
      </div>

      <div className="settings-content">
        <div className="settings-sections">
          {/* Model Settings */}
          <section className="settings-section">
            <h3>🤖 Model Settings</h3>

            <div className="setting-item">
              <label htmlFor="defaultModel">Default Model</label>
              <select
                id="defaultModel"
                name="defaultModel"
                value={formData.defaultModel}
                onChange={handleInputChange}
              >
                {appState.models.length === 0 ? (
                  <option value="">No models available</option>
                ) : (
                  appState.models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))
                )}
              </select>
              <p className="setting-description">
                Default AI model for chat and RAG queries
              </p>
            </div>

            <div className="setting-item">
              <label htmlFor="defaultMaxTokens">Default Max Tokens</label>
              <input
                id="defaultMaxTokens"
                name="defaultMaxTokens"
                type="number"
                min="100"
                max="4000"
                value={formData.defaultMaxTokens}
                onChange={handleInputChange}
              />
              <p className="setting-description">
                Maximum tokens for model responses (100-4000)
              </p>
            </div>

            <div className="setting-item">
              <label htmlFor="defaultTopK">Default Top K (RAG)</label>
              <input
                id="defaultTopK"
                name="defaultTopK"
                type="number"
                min="1"
                max="10"
                value={formData.defaultTopK}
                onChange={handleInputChange}
              />
              <p className="setting-description">
                Number of documents to retrieve for RAG queries (1-10)
              </p>
            </div>
          </section>

          {/* Appearance Settings */}
          <section className="settings-section">
            <h3>🎨 Appearance</h3>

            <div className="setting-item">
              <label htmlFor="theme">Theme</label>
              <select
                id="theme"
                name="theme"
                value={formData.theme}
                onChange={handleInputChange}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
              <p className="setting-description">
                Choose your preferred color theme
              </p>
            </div>
          </section>

          {/* Behavior Settings */}
          <section className="settings-section">
            <h3>⚡ Behavior</h3>

            <div className="setting-item checkbox-item">
              <label htmlFor="autoSave">
                <input
                  id="autoSave"
                  name="autoSave"
                  type="checkbox"
                  checked={formData.autoSave}
                  onChange={handleInputChange}
                />
                Auto-save conversations
              </label>
              <p className="setting-description">
                Automatically save chat history and RAG results
              </p>
            </div>

            <div className="setting-item checkbox-item">
              <label htmlFor="enableNotifications">
                <input
                  id="enableNotifications"
                  name="enableNotifications"
                  type="checkbox"
                  checked={formData.enableNotifications}
                  onChange={handleInputChange}
                />
                Enable notifications
              </label>
              <p className="setting-description">
                Show desktop notifications for completed operations
              </p>
            </div>

            <div className="setting-item">
              <label htmlFor="requestTimeout">Request Timeout (seconds)</label>
              <input
                id="requestTimeout"
                name="requestTimeout"
                type="number"
                min="10"
                max="120"
                value={formData.requestTimeout}
                onChange={handleInputChange}
              />
              <p className="setting-description">
                Timeout for API requests (10-120 seconds)
              </p>
            </div>
          </section>

          {/* Privacy & Data */}
          <section className="settings-section">
            <h3>🔒 Privacy & Data</h3>

            <div className="setting-item checkbox-item">
              <label htmlFor="enableTelemetry">
                <input
                  id="enableTelemetry"
                  name="enableTelemetry"
                  type="checkbox"
                  checked={formData.enableTelemetry}
                  onChange={handleInputChange}
                />
                Enable telemetry
              </label>
              <p className="setting-description">
                Send anonymous usage data to help improve Willow
              </p>
            </div>

            <div className="setting-item">
              <label htmlFor="maxCacheSize">Max Cache Size (MB)</label>
              <input
                id="maxCacheSize"
                name="maxCacheSize"
                type="number"
                min="50"
                max="1000"
                value={formData.maxCacheSize}
                onChange={handleInputChange}
              />
              <p className="setting-description">
                Maximum size for cached data (50-1000 MB)
              </p>
            </div>
          </section>

          {/* Import/Export */}
          <section className="settings-section">
            <h3>📦 Import/Export</h3>

            <div className="import-export-controls">
              <button
                type="button"
                className="export-button"
                onClick={exportSettings}
              >
                📤 Export Settings
              </button>

              <div className="import-container">
                <input
                  type="file"
                  accept=".json"
                  onChange={importSettings}
                  className="import-input"
                  id="import-settings"
                />
                <label htmlFor="import-settings" className="import-button">
                  📥 Import Settings
                </label>
              </div>

              <button
                type="button"
                className="defaults-button"
                onClick={handleDefaults}
              >
                🔄 Restore Defaults
              </button>
            </div>
          </section>
        </div>

        {/* Settings Summary */}
        <div className="settings-summary">
          <h3>📊 Configuration Summary</h3>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Model:</span>
              <span className="summary-value">
                {formData.defaultModel || "None"}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Max Tokens:</span>
              <span className="summary-value">{formData.defaultMaxTokens}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">RAG Top K:</span>
              <span className="summary-value">{formData.defaultTopK}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Theme:</span>
              <span className="summary-value">{formData.theme}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Auto-save:</span>
              <span className="summary-value">
                {formData.autoSave ? "On" : "Off"}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Telemetry:</span>
              <span className="summary-value">
                {formData.enableTelemetry ? "On" : "Off"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsInterface;
