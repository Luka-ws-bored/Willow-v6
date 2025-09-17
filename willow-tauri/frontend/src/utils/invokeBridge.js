import { invoke } from "@tauri-apps/api/core";

/**
 * normalizeArgs: maps camelCase client keys to backend expected keys.
 */
function normalizeArgs(args = {}) {
  const normalized = { ...args };

  // Map frontend parameter names to backend expected names
  if ("query" in normalized) {
    normalized.prompt = normalized.query;
    delete normalized.query;
  }
  if ("maxTokens" in normalized) {
    normalized.max_tokens = normalized.maxTokens;
    delete normalized.maxTokens;
  }
  if ("topK" in normalized) {
    normalized.top_k = normalized.topK;
    delete normalized.topK;
  }
  if ("modelName" in normalized) {
    normalized.model = normalized.modelName;
    delete normalized.modelName;
  }

  return normalized;
}

/**
 * invokeBackend - single place to call Rust commands:
 *   cmdName: string (the Rust command, e.g. query_willow_llm)
 *   args: object (client-side keys)
 */
export async function invokeBackend(cmdName, args = {}) {
  const normalized = normalizeArgs(args);
  try {
    return await invoke(cmdName, normalized);
  } catch (err) {
    console.error("invokeBackend error", cmdName, normalized, err);
    throw err;
  }
}

/**
 * Convenience mapping for legacy names to actual backend commands:
 */
export const api = {
  queryLLM: (args) => invokeBackend("query_willow_llm", args),
  queryRag: (args) => invokeBackend("query_willow_rag", args),
  getStatus: (args) => invokeBackend("get_willow_status", args),

  // Additional commands that may be needed
  queryRagSimple: (args) => invokeBackend("query_willow_rag", args),
  queryRagAdvanced: (args) => invokeBackend("query_willow_rag", args),
  addDocumentToRag: (args) => invokeBackend("add_document_to_rag", args),
  getSystemInfo: (args) => invokeBackend("get_system_info", args),
  getPerformanceMetrics: (args) =>
    invokeBackend("get_performance_metrics", args),
};
