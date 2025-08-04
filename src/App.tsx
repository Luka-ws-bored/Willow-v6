import { useQuery } from "convex/react";
import { api } from "../convex/_generated/api";
import { Toaster } from "sonner";
import { WillowChat } from "./WillowChat";
import { ConfigProvider } from "./contexts/ConfigContext";

export default function App() {
  return (
    <ConfigProvider>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-sm h-16 flex justify-between items-center border-b shadow-sm px-4">
          <h2 className="text-2xl font-bold text-blue-600">Willow v6 Chat</h2>
          <div className="text-sm text-gray-600">
            Session-based • No sign-in required
          </div>
        </header>
        <main className="flex-1 flex items-start justify-center p-4">
          <div className="w-full max-w-6xl mx-auto">
            <Content />
          </div>
        </main>
        <Toaster position="top-right" />
      </div>
    </ConfigProvider>
  );
}

function Content() {
  return (
    <div className="flex flex-col gap-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Welcome to Willow v6</h1>
        <p className="text-lg text-gray-600">
          Upload documents, configure MCPs, and ask questions with RAG-enhanced responses
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Featuring CrewAI orchestration, multimodal support, and environment configuration
        </p>
      </div>
      <WillowChat />
    </div>
  );
}
