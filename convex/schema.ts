import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";
import { authTables } from "@convex-dev/auth/server";

const applicationTables = {
  documents: defineTable({
    fileName: v.string(),
    fileId: v.id("_storage"),
    sessionId: v.string(),
    uploadedAt: v.number(),
    processed: v.boolean(),
  }).index("by_session", ["sessionId"]),
  
  chatMessages: defineTable({
    sessionId: v.string(),
    message: v.string(),
    response: v.string(),
    timestamp: v.number(),
    usedRetrieval: v.boolean(),
    mcpId: v.union(v.string(), v.null()),
  }).index("by_session", ["sessionId"]),
  
  documentChunks: defineTable({
    documentId: v.id("documents"),
    content: v.string(),
    chunkIndex: v.number(),
  }).index("by_document", ["documentId"]),

  multimodalFiles: defineTable({
    fileName: v.string(),
    fileId: v.id("_storage"),
    fileType: v.string(),
    mimeType: v.string(),
    uploadedAt: v.number(),
    processed: v.boolean(),
  }),

  crewTasks: defineTable({
    crewId: v.string(),
    taskDescription: v.string(),
    status: v.string(),
    result: v.optional(v.string()),
    error: v.optional(v.string()),
    createdAt: v.number(),
    completedAt: v.optional(v.number()),
  }).index("by_status", ["status"]),
};

export default defineSchema({
  ...authTables,
  ...applicationTables,
});
