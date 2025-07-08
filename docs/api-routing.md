# 🔄 API Routing & RAG Pipeline - Willow v6

## Overview

Willow v6 implements a sophisticated routing system that intelligently directs user queries through different processing pipelines based on intent, complexity, and available resources. The system is designed to maximize efficiency while maintaining high-quality responses through a combination of direct plugin processing and retrieval-augmented generation (RAG).

## Architecture

### Current Implementation (v6.0)

The current routing system operates on a **plugin-first** approach:

```
User Query → Intent Detection → Plugin Routing → Response
     ↓
[Plugin System] → [Direct Processing] → [Response]
```

### Future Implementation (v6.1+)

The enhanced routing system will implement a **multi-tier approach**:

```
User Query → Intent Detection → Route Decision → Processing Pipeline → Response
     ↓
[Plugin System] → [RAG Pipeline] → [Fallback System] → [Response]
```

## Route Structure

### 1. Direct → Plugins

**Priority: Highest**

- **When**: Query matches known plugin capabilities
- **How**: Direct invocation of specialized plugin functions
- **Examples**:
  - Color analysis → `color_mood_mapper`
  - Code debugging → `bug_buster`
  - SQL generation → `sql_sorcerer`
  - Prompt optimization → `prompt_checker`

### 2. Fallback → LangChain RAG

**Priority: Medium**

- **When**: Query requires knowledge not covered by plugins
- **How**: Retrieval-augmented generation using LangChain
- **Components**:
  - Vector database (ChromaDB/Pinecone)
  - Document embeddings
  - Context retrieval
  - LLM synthesis

### 3. Unknown → Default Error or GPT Call

**Priority: Lowest**

- **When**: Query cannot be processed by plugins or RAG
- **How**: Direct LLM call or structured error response
- **Fallback Options**:
  - OpenAI GPT-4/3.5
  - Claude API
  - Local model (Ollama/LM Studio)

## Technical Implementation

### Plugin Routing Logic

```python
def route_query(query: str) -> str:
    # 1. Intent detection
    intent = detect_intent(query)

    # 2. Plugin matching
    if plugin := find_matching_plugin(intent):
        return plugin.process(query)

    # 3. RAG fallback
    if should_use_rag(query):
        return rag_pipeline.process(query)

    # 4. Direct LLM fallback
    return direct_llm_call(query)
```

### Intent Detection

The system uses pattern matching and keyword analysis to determine query intent:

- **Plugin Keywords**: Specific terms that trigger plugin activation
- **Complexity Scoring**: Determines if RAG is needed
- **Domain Classification**: Routes to appropriate knowledge bases

### RAG Pipeline Components

#### Vector Database

- **Storage**: Document embeddings and metadata
- **Search**: Semantic similarity matching
- **Updates**: Incremental knowledge base updates

#### Document Processing

- **Ingestion**: PDF, Markdown, text files
- **Chunking**: Semantic text splitting
- **Embedding**: OpenAI/Claude embedding models

#### Retrieval & Generation

- **Context Retrieval**: Top-k relevant documents
- **Prompt Engineering**: Context-aware prompts
- **Response Synthesis**: LLM-based answer generation

## Future Enhancements

### v6.1 - RAGAS Integration

**RAGAS** (Retrieval-Augmented Generation Assessment) will be integrated for:

- **Factuality Scoring**: Evaluate response accuracy
- **Answer Relevance**: Measure response relevance to query
- **Context Precision**: Assess retrieved context quality
- **Context Recall**: Evaluate context completeness

### v6.2 - Advanced Routing

- **Learning Routes**: Adaptive routing based on user feedback
- **Performance Metrics**: Route optimization based on success rates
- **A/B Testing**: Compare different routing strategies

### v7.0 - Multi-Modal RAG

- **Image Processing**: Visual question answering
- **Audio Integration**: Speech-to-text RAG
- **Cross-Modal Retrieval**: Text-image-audio correlation

## Configuration

### Plugin Configuration

```yaml
active_plugins:
  - color_mood_mapper
  - bug_buster
  - sql_sorcerer
  - prompt_checker

plugin_routing:
  color_mood_mapper:
    keywords: ["color", "mood", "emotion", "feeling"]
    priority: 1
  bug_buster:
    keywords: ["bug", "error", "debug", "fix"]
    priority: 2
```

### RAG Configuration

```yaml
rag_pipeline:
  enabled: true
  vector_db: "chromadb"
  embedding_model: "text-embedding-3-small"
  retrieval_top_k: 5
  max_context_length: 4000
```

## Performance Considerations

### Latency Optimization

- **Plugin Caching**: Cache frequently used plugin results
- **Vector Index**: Optimized similarity search
- **Parallel Processing**: Concurrent plugin and RAG execution

### Cost Management

- **Token Budgeting**: Limit expensive LLM calls
- **Smart Fallbacks**: Use cheaper models when appropriate
- **Caching Strategy**: Store and reuse expensive computations

### Scalability

- **Horizontal Scaling**: Multiple RAG instances
- **Load Balancing**: Distribute queries across nodes
- **Database Sharding**: Partition vector databases

## Monitoring & Analytics

### Metrics Tracked

- **Route Distribution**: Which routes are used most
- **Success Rates**: Plugin vs RAG vs fallback performance
- **Response Times**: Latency by route type
- **User Satisfaction**: Feedback scores by route

### Logging

- **Query Logs**: Full query processing pipeline
- **Route Decisions**: Why specific routes were chosen
- **Performance Data**: Timing and resource usage
- **Error Tracking**: Failed routes and recovery

## Integration Points

### External APIs

- **OpenAI**: GPT models and embeddings
- **Claude**: Alternative LLM provider
- **Pinecone**: Vector database (optional)
- **ChromaDB**: Local vector database

### Internal Systems

- **Plugin Registry**: Dynamic plugin discovery
- **Config Management**: Runtime configuration updates
- **Logging System**: Centralized logging and monitoring
- **Cache Layer**: Response and embedding caching

## Development Roadmap

### Phase 1 (v6.0) - Current

- ✅ Plugin routing system
- ✅ Basic intent detection
- ✅ Configuration management

### Phase 2 (v6.1) - RAG Foundation

- 🔄 LangChain integration
- 🔄 Vector database setup
- 🔄 Basic RAG pipeline
- 🔄 RAGAS evaluation

### Phase 3 (v6.2) - Advanced Features

- 📋 Learning routes
- 📋 Performance optimization
- 📋 Advanced monitoring
- 📋 Multi-modal support

### Phase 4 (v7.0) - Production Ready

- 📋 Enterprise features
- 📋 Advanced security
- 📋 Full multi-modal RAG
- 📋 Distributed deployment

---

_This document will be updated as the RAG pipeline implementation progresses._
