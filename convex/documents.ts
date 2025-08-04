import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});

export const saveDocument = mutation({
  args: {
    fileName: v.string(),
    fileId: v.id("_storage"),
    sessionId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const documentId = await ctx.db.insert("documents", {
      fileName: args.fileName,
      fileId: args.fileId,
      sessionId: args.sessionId || `session_${Date.now()}`,
      uploadedAt: Date.now(),
      processed: false,
    });

    return documentId;
  },
});

export const getUserDocuments = query({
  args: {},
  handler: async (ctx) => {
    // Return empty array since we're not using user auth
    return [];
  },
});

export const getSessionDocuments = query({
  args: {
    sessionId: v.string(),
  },
  handler: async (ctx, args) => {
    const documents = await ctx.db
      .query("documents")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("desc")
      .collect();

    return documents;
  },
});

export const deleteDocument = mutation({
  args: {
    documentId: v.id("documents"),
  },
  handler: async (ctx, args) => {
    const document = await ctx.db.get(args.documentId);
    if (!document) {
      throw new Error("Document not found");
    }

    // Delete document chunks
    const chunks = await ctx.db
      .query("documentChunks")
      .withIndex("by_document", (q) => q.eq("documentId", args.documentId))
      .collect();

    for (const chunk of chunks) {
      await ctx.db.delete(chunk._id);
    }

    // Delete the document
    await ctx.db.delete(args.documentId);
    
    // Delete from storage
    await ctx.storage.delete(document.fileId);
  },
});
