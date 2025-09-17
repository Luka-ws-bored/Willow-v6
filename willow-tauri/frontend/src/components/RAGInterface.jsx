import React, { useState, useRef, useEffect } from "react";
import { api } from "../utils/invokeBridge";
import "./RAGInterface.css";

const RAGInterface = ({ appState, setIsLoading }) => {
  const [query, setQuery] = useState("");
  const [documents, setDocuments] = useState("");
  const [results, setResults] = useState([]);
  const [topK, setTopK] = useState(appState.settings.defaultTopK || 3);
  const [ragMode, setRagMode] = useState("simple"); // 'simple' or 'advanced'
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);

    try {
      let response;

      if (ragMode === "simple" && documents.trim()) {
        // Use simple RAG with provided documents
        const docArray = documents
          .split("\n")
          .filter((doc) => doc.trim())
          .map((doc) => doc.trim());

        response = await api.queryRag({
          prompt: query.trim(),
          documents: docArray,
          top_k: parseInt(topK),
        });
      } else {
        // Use advanced RAG with stored documents
        response = await api.queryRag({
          prompt: query.trim(),
          top_k: parseInt(topK),
        });
      }

      const result = {
        id: Date.now(),
        query: query.trim(),
        response: response.success ? response.data : `Error: ${response.error}`,
        timestamp: new Date(),
        mode: ragMode,
        success: response.success,
        topK: parseInt(topK),
      };

      setResults((prev) => [result, ...prev]);
      setQuery("");
    } catch (error) {
      const errorResult = {
        id: Date.now(),
        query: query.trim(),
        response: `Failed to get RAG response: ${error.message}`,
        timestamp: new Date(),
        mode: ragMode,
        success: false,
        topK: parseInt(topK),
      };

      setResults((prev) => [errorResult, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setIsLoading(true);

    try {
      for (const file of files) {
        const text = await file.text();
        await api.addDocumentToRag({
          content: text,
          metadata: {
            filename: file.name,
            size: file.size,
            type: file.type,
            uploaded: new Date().toISOString(),
          },
        });
      }

      alert(
        `Successfully uploaded ${files.length} document(s) to RAG database`
      );
    } catch (error) {
      alert(`Failed to upload documents: ${error.message}`);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const clearResults = () => {
    setResults([]);
  };

  const clearDocuments = () => {
    setDocuments("");
  };

  const formatTimestamp = (timestamp) => {
    return new Intl.DateTimeFormat("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(timestamp);
  };

  const isRagAvailable =
    appState.capabilities.rag_simple || appState.capabilities.rag_full;

  if (!isRagAvailable) {
    return (
      <div className="rag-interface">
        <div className="rag-unavailable">
          <div className="unavailable-icon">📚</div>
          <h3>RAG Not Available</h3>
          <p>
            RAG (Retrieval-Augmented Generation) functionality is not available.
          </p>
          <p>Please ensure RAG dependencies are installed:</p>
          <code>pip install faiss-cpu sentence-transformers</code>
        </div>
      </div>
    );
  }

  return (
    <div className="rag-interface">
      <div className="rag-header">
        <div className="rag-title">
          <h2>📚 RAG Interface</h2>
          <span className="rag-subtitle">Document-augmented queries</span>
        </div>

        <div className="rag-controls">
          <div className="mode-selector">
            <label htmlFor="rag-mode">Mode:</label>
            <select
              id="rag-mode"
              value={ragMode}
              onChange={(e) => setRagMode(e.target.value)}
            >
              <option value="simple">Simple (Inline Docs)</option>
              <option value="advanced">Advanced (Stored Docs)</option>
            </select>
          </div>

          <div className="topk-input">
            <label htmlFor="top-k">Top K:</label>
            <input
              id="top-k"
              type="number"
              min="1"
              max="10"
              value={topK}
              onChange={(e) => setTopK(e.target.value)}
            />
          </div>

          <button
            type="button"
            className="clear-button"
            onClick={clearResults}
            disabled={results.length === 0}
          >
            🗑️ Clear Results
          </button>
        </div>
      </div>

      <div className="rag-content">
        {ragMode === "simple" && (
          <div className="documents-section">
            <div className="section-header">
              <h3>📄 Documents</h3>
              <button
                type="button"
                className="clear-docs-button"
                onClick={clearDocuments}
                disabled={!documents.trim()}
              >
                Clear
              </button>
            </div>
            <textarea
              value={documents}
              onChange={(e) => setDocuments(e.target.value)}
              placeholder="Enter documents, one per line..."
              rows="6"
              className="documents-textarea"
            />
          </div>
        )}

        {ragMode === "advanced" && (
          <div className="file-upload-section">
            <div className="section-header">
              <h3>📁 Upload Documents</h3>
            </div>
            <div className="file-upload-area">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".txt,.md,.json"
                onChange={handleFileUpload}
                className="file-input"
              />
              <p className="upload-hint">
                Select .txt, .md, or .json files to add to RAG database
              </p>
            </div>
          </div>
        )}

        <form className="query-form" onSubmit={handleSubmit}>
          <div className="query-input-container">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query here..."
              rows="3"
              className="query-textarea"
              disabled={!appState.isConnected}
            />
            <button
              type="submit"
              className="query-button"
              disabled={
                !query.trim() ||
                !appState.isConnected ||
                (ragMode === "simple" && !documents.trim())
              }
            >
              <span className="query-icon">🔍</span>
              Query RAG
            </button>
          </div>

          {!appState.isConnected && (
            <div className="connection-warning">
              ⚠️ Not connected to Willow backend
            </div>
          )}

          {ragMode === "simple" && !documents.trim() && (
            <div className="documents-warning">
              ⚠️ Please provide documents for simple RAG mode
            </div>
          )}
        </form>

        <div className="results-section">
          <h3>🎯 Results</h3>
          {results.length === 0 ? (
            <div className="empty-results">
              <div className="empty-icon">🤔</div>
              <p>No RAG queries yet. Enter a query above to get started.</p>
            </div>
          ) : (
            <div className="results-list">
              {results.map((result) => (
                <div
                  key={result.id}
                  className={`result-item ${
                    result.success ? "success" : "error"
                  }`}
                >
                  <div className="result-header">
                    <div className="result-meta">
                      <span className="result-mode">{result.mode}</span>
                      <span className="result-topk">K={result.topK}</span>
                      <span className="result-timestamp">
                        {formatTimestamp(result.timestamp)}
                      </span>
                    </div>
                    <div className="result-status">
                      {result.success ? "✅" : "❌"}
                    </div>
                  </div>

                  <div className="result-query">
                    <strong>Query:</strong> {result.query}
                  </div>

                  <div className="result-response">
                    <strong>Response:</strong>
                    <div className="response-content">{result.response}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RAGInterface;
