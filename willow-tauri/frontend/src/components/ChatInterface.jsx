import React, { useState, useEffect, useRef } from "react";
import { api } from "../utils/invokeBridge";
import "./ChatInterface.css";

const ChatInterface = ({ appState, setIsLoading }) => {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [maxTokens, setMaxTokens] = useState(
    appState.settings.defaultMaxTokens || 1000
  );
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (appState.models.length > 0 && !selectedModel) {
      setSelectedModel(appState.settings.defaultModel || appState.models[0]);
    }
  }, [appState.models, selectedModel, appState.settings.defaultModel]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim() || !selectedModel) return;

    const userMessage = {
      id: Date.now(),
      type: "user",
      content: inputText.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      const response = await api.queryLLM({
        prompt: inputText.trim(),
        model: selectedModel,
        max_tokens: parseInt(maxTokens),
      });

      const assistantMessage = {
        id: Date.now() + 1,
        type: "assistant",
        content: response.success ? response.data : `Error: ${response.error}`,
        timestamp: new Date(),
        model: selectedModel,
        success: response.success,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: "error",
        content: `Failed to get response: ${error.message}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const formatTimestamp = (timestamp) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(timestamp);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-title">
          <h2>💬 Chat Interface</h2>
          <span className="chat-subtitle">Interact with AI models</span>
        </div>

        <div className="chat-controls">
          <div className="model-selector">
            <label htmlFor="model-select">Model:</label>
            <select
              id="model-select"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={appState.models.length === 0}
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
          </div>

          <div className="tokens-input">
            <label htmlFor="max-tokens">Max Tokens:</label>
            <input
              id="max-tokens"
              type="number"
              min="100"
              max="4000"
              value={maxTokens}
              onChange={(e) => setMaxTokens(e.target.value)}
            />
          </div>

          <button
            type="button"
            className="clear-button"
            onClick={clearChat}
            disabled={messages.length === 0}
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💭</div>
            <h3>Start a conversation</h3>
            <p>Type a message below to begin chatting with the AI.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.type} ${
                message.success === false ? "error" : ""
              }`}
            >
              <div className="message-header">
                <span className="message-sender">
                  {message.type === "user"
                    ? "👤 You"
                    : message.type === "assistant"
                    ? "🤖 Assistant"
                    : "⚠️ Error"}
                </span>
                <span className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </span>
                {message.model && (
                  <span className="message-model">({message.model})</span>
                )}
              </div>
              <div className="message-content">{message.content}</div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <div className="input-container">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here... (Press Enter to send, Shift+Enter for new line)"
            rows="3"
            disabled={!appState.isConnected || appState.models.length === 0}
          />
          <button
            type="submit"
            className="send-button"
            disabled={
              !inputText.trim() || !selectedModel || !appState.isConnected
            }
          >
            <span className="send-icon">📤</span>
            Send
          </button>
        </div>

        {!appState.isConnected && (
          <div className="connection-warning">
            ⚠️ Not connected to Willow backend
          </div>
        )}

        {appState.models.length === 0 && appState.isConnected && (
          <div className="models-warning">⚠️ No models available</div>
        )}
      </form>
    </div>
  );
};

export default ChatInterface;
