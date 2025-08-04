import React, { useState, useRef, useEffect } from "react";
import { useMutation, useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import { toast } from "sonner";
import ReactMarkdown from 'react-markdown';
import { ConfigPanel } from "./components/ConfigPanel";
import { MCPSelector, MCP } from "./components/MCPSelector";
import { MultimodalUpload } from "./components/MultimodalUpload";
import { CrewAIPanel } from "./components/CrewAIPanel";

export function WillowChat() {
  const [message, setMessage] = useState("");
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random()}`);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedMCP, setSelectedMCP] = useState<MCP | null>(null);
  const [isSending, setIsSending] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const documents = useQuery(api.documents.getSessionDocuments, { sessionId }) || [];
  const chatHistory = useQuery(api.chat.getChatHistory, { sessionId }) || [];
  
  const generateUploadUrl = useMutation(api.documents.generateUploadUrl);
  const saveDocument = useMutation(api.documents.saveDocument);
  const deleteDocument = useMutation(api.documents.deleteDocument);
  const sendMessage = useMutation(api.chat.sendMessage);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    
    try {
      for (const file of Array.from(files)) {
        // Generate upload URL
        const uploadUrl = await generateUploadUrl();
        
        // Upload file
        const result = await fetch(uploadUrl, {
          method: "POST",
          headers: { "Content-Type": file.type },
          body: file,
        });

        if (!result.ok) {
          throw new Error(`Upload failed for ${file.name}`);
        }

        const { storageId } = await result.json();
        
        // Save document metadata
        await saveDocument({
          fileName: file.name,
          fileId: storageId,
        });
      }
      
      toast.success(`Successfully uploaded ${files.length} document(s)`);
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      console.error("Upload error:", error);
      toast.error("Failed to upload documents");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isSending) return;

    const userMessage = message.trim();
    setMessage("");
    setIsSending(true);

    try {
      await sendMessage({
        message: userMessage,
        sessionId,
        mcpId: selectedMCP?.id,
      });
    } catch (error) {
      console.error("Send message error:", error);
      toast.error("Failed to send message");
    } finally {
      setIsSending(false);
    }
  };

  const handleDeleteDocument = async (documentId: any) => {
    try {
      await deleteDocument({ documentId });
      toast.success("Document deleted successfully", {
        action: {
          label: "Undo",
          onClick: () => toast.info("Undo functionality coming soon!")
        }
      });
    } catch (error) {
      console.error("Delete error:", error);
      toast.error("Failed to delete document");
    }
  };

  const handleMultimodalUpload = (files: any[]) => {
    toast.success(`Uploaded ${files.length} multimodal file(s) - ready for processing`);
  };

  const isWaitingForResponse = chatHistory.some(chat => !chat.response);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Configuration Panel */}
      <ConfigPanel />

      {/* MCP Selector */}
      <MCPSelector selectedMCP={selectedMCP} onMCPSelect={setSelectedMCP} />

      {/* CrewAI Panel */}
      <CrewAIPanel />

      {/* Multimodal Upload */}
      <MultimodalUpload 
        onFilesUploaded={handleMultimodalUpload}
        isUploading={isUploading}
        setIsUploading={setIsUploading}
      />

      {/* Document Upload Section */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Document Upload</h2>
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.pdf,.doc,.docx,.md"
              onChange={handleFileUpload}
              disabled={isUploading}
              className="flex-1 text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
            />
            {isUploading && (
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <span className="text-sm text-gray-600">Uploading...</span>
              </div>
            )}
          </div>
          
          {documents.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Uploaded Documents:</h3>
              <div className="space-y-1">
                {documents.map((doc) => (
                  <div key={doc._id} className="flex items-center justify-between bg-gray-50 rounded p-2">
                    <span className="text-sm text-gray-700">{doc.fileName}</span>
                    <button
                      onClick={() => handleDeleteDocument(doc._id)}
                      className="text-red-600 hover:text-red-800 text-sm transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Section */}
      <div className="bg-white rounded-lg shadow-sm border">
        {/* Chat History */}
        <div className="p-6 border-b max-h-96 overflow-y-auto">
          {chatHistory.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              <p>No messages yet. Ask Willow a question to get started!</p>
              {documents.length > 0 && (
                <p className="text-sm mt-2">Your documents are ready for RAG-enhanced responses.</p>
              )}
              {selectedMCP && (
                <p className="text-sm mt-2 text-blue-600">
                  MCP Selected: {selectedMCP.name}
                </p>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {chatHistory.map((chat) => (
                <div key={chat._id} className="space-y-2">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <p className="text-gray-800">{chat.message}</p>
                    {chat.mcpId && (
                      <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        MCP: {chat.mcpId}
                      </span>
                    )}
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    {chat.response ? (
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown>{chat.response}</ReactMarkdown>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-gray-500">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-400"></div>
                        <span>Willow is thinking...</span>
                      </div>
                    )}
                    {chat.response && chat.usedRetrieval && (
                      <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                        RAG Enhanced
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <div className="p-6">
          <form onSubmit={handleSendMessage} className="space-y-4">
            <div className="flex gap-3">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Ask Willow a question..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                disabled={isWaitingForResponse || isSending}
              />
              <button
                type="submit"
                disabled={!message.trim() || isWaitingForResponse || isSending}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
              >
                {isSending && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                )}
                Ask Willow
              </button>
            </div>
            <div className="flex flex-wrap gap-2 text-sm text-gray-500">
              <span>
                {documents.length > 0 
                  ? `Ready to use RAG with ${documents.length} document(s).`
                  : "Upload documents above to enable RAG functionality."
                }
              </span>
              {selectedMCP && (
                <span className="text-blue-600">
                  • Using {selectedMCP.name} MCP
                </span>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
