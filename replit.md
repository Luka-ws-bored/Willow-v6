# Overview

Willow v6 is a comprehensive AI automation framework designed for power users, hackers, and indie agents. It provides a modular, plugin-based architecture that bridges local AI models, cloud APIs, and GUI workflows into one intelligent system. The framework features dynamic plugin loading, intelligent routing between different processing pipelines, and multimodal capabilities (planned). The system is built to be highly configurable and extensible, allowing users to customize their AI assistant experience through plugins and configuration files.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Framework Design
The system follows a modular, plugin-first architecture with intelligent routing capabilities. The main entry point (`willow.py`) initializes core components including memory management, plugin loading, and interface routing. The architecture separates concerns through distinct modules for memory persistence, plugin management, intent routing, and RAG (Retrieval-Augmented Generation) processing.

## Plugin System
Willow uses a dynamic plugin loading system where plugins are Python modules located in the `prompts/` directory. The `plugin_loader.py` module reads configuration from `config.yaml` to determine which plugins to load at runtime. Plugins include specialized tools like `bug_buster` for code analysis, `sql_sorcerer` for SQL generation, `color_mood_mapper` for mood-to-color mapping, and `prompt_checker` for prompt optimization. Each plugin implements specific functionality and can be enabled/disabled through configuration.

## Intelligent Routing
The system implements a multi-tier routing approach through the `intent_router.py` and `rag_router.py` modules. User queries are analyzed to determine the appropriate processing pipeline: direct plugin execution for specialized tasks, RAG pipeline for knowledge-based queries requiring document retrieval, or fallback to general LLM processing. This routing system ensures optimal response generation based on query intent and complexity.

## Memory Management
The `memory.py` module provides JSON-based persistent storage for conversation history, events, and system interactions. The memory system supports automatic timestamping, file persistence, and querying capabilities. Memory entries are used by the subconscious system for periodic summarization and analysis.

## RAG Pipeline
The RAG system leverages LangChain for document processing and retrieval. It supports multiple vector stores (FAISS, ChromaDB) and can process documents from local directories. The RAG pipeline integrates with multiple LLM providers and provides fallback mechanisms for robust operation.

## Interface System
The framework supports both CLI and GUI interfaces through the `interface_router.py` module. Interface selection is configurable, and the system includes a PyQt6-based GUI implementation (from v5.1) alongside the primary CLI interface. The interface router handles initialization of the appropriate mode based on configuration.

## Subconscious Agent
The `subconscious.py` module implements a background agent that periodically processes memory data to generate summaries and insights. This system can evaluate multiple provider responses and select the best output, providing a form of meta-cognitive processing.

# External Dependencies

## LLM Providers
The system integrates with multiple LLM providers including OpenAI GPT models, Google Gemini, Claude (Anthropic), Mistral, and Groq. Provider selection is configurable with intelligent fallback mechanisms. The system supports both direct API access and reverse proxy routing through services like OpenRouter.

## Local Model Integration
Willow supports local model backends including LM Studio and Ollama for offline operation. The system can route queries to local models as primary or fallback options based on configuration.

## Vector Database
The RAG system uses FAISS for local vector storage with planned support for cloud-based solutions like Pinecone and ChromaDB. Vector embeddings are generated using OpenAI's embedding models.

## Document Processing
LangChain is used for document loading, text splitting, and retrieval chain construction. The system can process various document formats and maintains document indexes for efficient retrieval.

## Configuration Management
YAML configuration files control system behavior, plugin activation, and provider preferences. Environment variables manage sensitive API keys through `.env` files.

## Third-Party Libraries
Key dependencies include PyQt6 for GUI development, Rich for enhanced console output, gTTS for text-to-speech capabilities, requests for HTTP operations, and various AI/ML libraries for model integration. The system also uses tiktoken for token counting and trafilatura for web content extraction.