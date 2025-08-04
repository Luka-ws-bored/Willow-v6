import { internalAction, internalMutation, mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { api, internal } from "./_generated/api";

export const sendMessage = mutation({
  args: {
    message: v.string(),
    sessionId: v.string(),
    mcpId: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // Schedule the AI response
    await ctx.scheduler.runAfter(0, internal.chat.generateResponse, {
      message: args.message,
      sessionId: args.sessionId,
      mcpId: args.mcpId || null,
    });

    return { success: true };
  },
});

export const generateResponse = internalAction({
  args: {
    message: v.string(),
    sessionId: v.string(),
    mcpId: v.union(v.string(), v.null()),
  },
  handler: async (ctx, args) => {
    try {
      // Get documents for RAG (session-based, no user auth required)
      const documents = await ctx.runQuery(api.documents.getSessionDocuments, {
        sessionId: args.sessionId
      });
      
      let response = "";
      let usedRetrieval = false;

      if (documents.length > 0) {
        // Use RAG with documents
        response = await generateRAGResponse(args.message, documents, args.mcpId);
        usedRetrieval = true;
      } else {
        // Fallback to direct LLM response
        response = await generateLLMResponse(args.message, args.mcpId);
        usedRetrieval = false;
      }

      // Save the conversation
      await ctx.runMutation(internal.chat.saveChatMessage, {
        sessionId: args.sessionId,
        message: args.message,
        response,
        usedRetrieval,
        mcpId: args.mcpId,
      });

    } catch (error) {
      console.error("Error generating response:", error);
      
      // Save error response
      await ctx.runMutation(internal.chat.saveChatMessage, {
        sessionId: args.sessionId,
        message: args.message,
        response: "I apologize, but I encountered an error processing your request. Please try again.",
        usedRetrieval: false,
        mcpId: args.mcpId,
      });
    }
  },
});

export const saveChatMessage = internalMutation({
  args: {
    sessionId: v.string(),
    message: v.string(),
    response: v.string(),
    usedRetrieval: v.boolean(),
    mcpId: v.union(v.string(), v.null()),
  },
  handler: async (ctx, args) => {
    await ctx.db.insert("chatMessages", {
      sessionId: args.sessionId,
      message: args.message,
      response: args.response,
      timestamp: Date.now(),
      usedRetrieval: args.usedRetrieval,
      mcpId: args.mcpId,
    });
  },
});

export const getChatHistory = query({
  args: {
    sessionId: v.string(),
  },
  handler: async (ctx, args) => {
    const messages = await ctx.db
      .query("chatMessages")
      .withIndex("by_session", (q) => q.eq("sessionId", args.sessionId))
      .order("asc")
      .collect();

    return messages;
  },
});

export const saveMultimodalFile = mutation({
  args: {
    fileName: v.string(),
    fileId: v.id("_storage"),
    fileType: v.string(),
    mimeType: v.string(),
  },
  handler: async (ctx, args) => {
    const fileId = await ctx.db.insert("multimodalFiles", {
      fileName: args.fileName,
      fileId: args.fileId,
      fileType: args.fileType,
      mimeType: args.mimeType,
      uploadedAt: Date.now(),
      processed: false,
    });

    return fileId;
  },
});

// Helper functions for AI responses
async function generateRAGResponse(message: string, documents: any[], mcpId: string | null): Promise<string> {
  const retrievalK = process.env.RETRIEVAL_K || "5";
  const mcpContext = mcpId ? `\n\n**MCP Context (${mcpId}):** This response is enhanced with the ${mcpId} Model Context Protocol for specialized processing.` : "";
  
  return `## RAG-Enhanced Response

**Query:** "${message}"

**Context:** Based on your uploaded documents (using top ${retrievalK} relevant chunks)${mcpContext}

**Analysis:** This is a comprehensive RAG-enhanced response that would:
1. Analyze your documents for relevant context
2. Extract key information related to your query
3. Synthesize insights from multiple sources
4. Provide contextual answers with citations

**Key Findings:**
- Document analysis reveals relevant patterns
- Cross-referenced information provides deeper insights
- Contextual understanding enhanced by RAG retrieval

*This response demonstrates the RAG functionality. In a production environment, this would integrate with your actual document processing and LLM systems.*`;
}

async function generateLLMResponse(message: string, mcpId: string | null): Promise<string> {
  const llmMode = process.env.LLM_MODE || "local";
  const modelName = process.env.MODEL_NAME || "default";
  const mcpContext = mcpId ? `\n\n**MCP Enhancement:** Using ${mcpId} protocol for specialized processing.` : "";
  
  return `## Standard LLM Response

**Query:** "${message}"

**Configuration:** Using ${llmMode} mode with ${modelName} model${mcpContext}

**Response:** This is a fallback LLM response that would normally be generated by your configured language model. 

**Recommendations:**
- Upload documents to enable RAG functionality
- Configure environment variables for optimal performance
- Consider using MCPs for specialized tasks

*To get RAG-enhanced responses, please upload relevant documents above.*`;
}
