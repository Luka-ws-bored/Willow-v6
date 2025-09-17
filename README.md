[![CI](https://github.com/Luka-ws-bored/Willow-v6/actions/workflows/test.yml/badge.svg)](https://github.com/Luka-ws-bored/Willow-v6/actions)
[![Coverage](https://img.shields.io/codecov/c/github/Luka-ws-bored/Willow-v6?logo=codecov)](https://codecov.io/gh/Luka-ws-bored/Willow-v6)

# Willow v6.0.0

A powerful local-first AI automation framework with advanced RAG (Retrieval-Augmented Generation) capabilities, designed for seamless fallback between multiple LLM providers and intelligent document processing.

## 🌟 Key Features

- **🤖 Multi-Provider LLM Support**: Seamless fallback between OpenAI, Claude, Gemini, Mistral, and local models
- **📚 Advanced RAG Pipeline**: Retrieval-augmented generation with vector database integration
- **⚡ Async/Await Support**: High-performance async operations throughout
- **🛡️ Security-First Design**: Input validation, path sanitization, and secure file operations
- **🎯 Graceful Degradation**: Core functionality works without optional dependencies
- **📊 Performance Monitoring**: Built-in metrics, caching, and optimization
- **🔧 Modular Architecture**: Plugin-based system with customizable components
- **🌐 Multi-Interface**: CLI, GUI, API, and native desktop app support
- **🖥️ Desktop Application**: Native cross-platform desktop app built with Tauri
- **🔄 Enhanced Retry Logic**: Exponential backoff with circuit breaker pattern for robust operations
- **📈 Structured Telemetry**: JSON logging and comprehensive metrics tracking
- **⚡ Batch Processing**: Async batch document processing with concurrency control
- **💾 Advanced Caching**: TTL-based caching with LRU eviction for improved performance

## 🚀 Quick Start

### Basic Installation

```bash
git clone https://github.com/Luka-ws-bored/Willow-v6.git
cd Willow-v6
pip install -r requirements.txt
```

### Optional RAG Dependencies

For advanced document retrieval and semantic search capabilities:

```bash
# Install RAG dependencies (optional)
pip install -r requirements-rag.txt
```

### Optional Enhancement Dependencies

For advanced features like structured telemetry, document similarity, and comprehensive testing:

```bash
# Install enhancement dependencies (optional)
pip install scikit-learn datasets ragas  # For evaluation and similarity processing
pip install pytest pytest-asyncio         # For comprehensive testing
```

### Running Willow

```bash
# Basic usage
python willow.py

# Or use the main module
python -m src.main

# Run demonstration
python demo_rag_integration.py
```

### Desktop Application

For a native desktop experience, Willow v6 includes a Tauri-based desktop application:

```bash
# Navigate to the desktop app directory
cd willow-tauri

# Run setup (installs Node.js and Rust dependencies)
# Windows:
setup.bat

# macOS/Linux:
chmod +x setup.sh
./setup.sh

# Run in development mode
npm run tauri:dev

# Build for production
npm run tauri:build
```

## 📖 Usage Examples

### Basic LLM Queries

```python
from src.main import query_llm, async_query_llm
import asyncio

# Synchronous query
response = query_llm("What is artificial intelligence?")
print(response)

# Asynchronous query
async def main():
    response = await async_query_llm("Explain machine learning")
    print(response)

asyncio.run(main())
```

### RAG-Enhanced Queries

```python
from src.main import async_query_rag_simple, RAG_AVAILABLE
from src.rag_pipeline import create_rag_pipeline
import asyncio

# Check if RAG is available
if RAG_AVAILABLE:
    print("✅ RAG functionality enabled")
else:
    print("⚠️ RAG dependencies not installed - using standard LLM")

# Quick RAG with documents
async def quick_rag_example():
    documents = [
        "Willow v6 is an AI automation framework with RAG capabilities.",
        "It supports multiple LLM providers and async operations.",
        "The system includes security features and performance optimization."
    ]

    response = await async_query_rag_simple(
        "What are Willow's main features?",
        documents=documents
    )
    print(f"RAG Response: {response}")

# Persistent RAG database
def persistent_rag_example():
    # Create RAG pipeline with persistent storage
    rag = create_rag_pipeline(db_path="./my_knowledge_base")

    # Add documents with metadata
    documents = [
        "Python is a high-level programming language.",
        "Machine learning uses algorithms to learn from data."
    ]
    metadata = [
        {"topic": "programming", "language": "python"},
        {"topic": "ai", "subtopic": "machine_learning"}
    ]

    rag.add_documents(documents, metadata)

    # Query with context formatting
    result = rag.query_with_context("Tell me about Python", top_k=2)
    print(f"Context: {result['context']}")
    print(f"Found {result['document_count']} relevant documents")

# Run examples
if __name__ == "__main__":
    asyncio.run(quick_rag_example())
    persistent_rag_example()
```

### Batch Processing

```python
from src.main import batch_query_llm, batch_query_rag
import asyncio

# Batch LLM queries
prompts = [
    "What is Python?",
    "Explain JavaScript",
    "Compare Python and JavaScript"
]

# Synchronous batch
responses = batch_query_llm(prompts)
for i, response in enumerate(responses):
    print(f"Response {i+1}: {response}")

# Asynchronous RAG batch
async def batch_rag_example():
    responses = await batch_query_rag(prompts)
    for i, response in enumerate(responses):
        print(f"RAG Response {i+1}: {response}")

asyncio.run(batch_rag_example())
```

### Enhanced Features (Optional)

#### Structured Telemetry and Metrics

```python
from src.utils.logging_config import (
    setup_willow_logging, TelemetryContext, AsyncTelemetryContext,
    get_rag_metrics, export_telemetry_data
)
from pathlib import Path

# Setup enhanced logging with JSON telemetry
logger = setup_willow_logging(
    log_level="INFO",
    log_file=Path("./logs/willow.log"),
    enable_performance_tracking=True,
    enable_json_telemetry=True,
    json_telemetry_file=Path("./logs/telemetry.json")
)

# Use telemetry context for tracking operations
with TelemetryContext("document_processing", pipeline="batch_processor") as telemetry:
    # Your processing code here
    telemetry.set_cache_hit(True)
    telemetry.metadata["documents_processed"] = 150

# Async telemetry tracking
async def async_with_telemetry():
    async with AsyncTelemetryContext("rag_query", pipeline="vector_search") as telemetry:
        result = await async_query_rag_simple("What is AI?")
        telemetry.metadata["query_tokens"] = len(result.split())
        return result

# Get comprehensive metrics
metrics = get_rag_metrics(logger)
print(f"Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")
print(f"Average response time: {metrics.get('avg_retrieval_time', 0):.3f}s")

# Export telemetry data
telemetry_json = export_telemetry_data(logger, format='json')
print(f"Exported telemetry: {len(telemetry_json)} characters")
```

#### Async Batch Document Processing

```python
from src.utils.async_helpers import (
    DocumentBatchProcessor, async_rag_document_ingestion,
    async_batch_file_processing, async_document_similarity_batch
)
from pathlib import Path

# Batch document processing
async def batch_processing_example():
    processor = DocumentBatchProcessor(max_concurrent=4, chunk_size=50)

    # Process documents from files
    file_paths = [Path("doc1.txt"), Path("doc2.txt"), Path("doc3.txt")]

    async def document_processor(content: str) -> dict:
        # Process document content
        return {
            "word_count": len(content.split()),
            "processed": True,
            "timestamp": time.time()
        }

    results = await processor.process_documents_from_files(
        file_paths=file_paths,
        processor_func=document_processor,
        validate_paths=True  # Security validation
    )

    for file_path, result, error in results:
        if error:
            print(f"Error processing {file_path}: {error}")
        else:
            print(f"Processed {file_path}: {result['word_count']} words")

    # Get processing statistics
    stats = processor.get_stats()
    print(f"Processed {stats['documents_processed']} documents")
    print(f"Average processing time: {stats.get('avg_processing_time', 0):.3f}s")

# RAG document ingestion
async def rag_ingestion_example():
    documents = ["Document 1 content", "Document 2 content"]
    metadata = [{"category": "tech"}, {"category": "science"}]

    stats = await async_rag_document_ingestion(
        documents=documents,
        metadatas=metadata,
        batch_size=10,
        max_concurrent=3
    )

    print(f"Ingested {stats['successful_adds']} documents successfully")
    print(f"Processing time: {stats['processing_time']:.2f}s")

# Document similarity processing
async def similarity_example():
    query_docs = ["Machine learning algorithms", "Neural networks"]
    reference_docs = ["AI and ML overview", "Deep learning basics", "Data science"]

    similarities = await async_document_similarity_batch(
        query_docs=query_docs,
        reference_docs=reference_docs,
        similarity_threshold=0.5,
        max_concurrent=2
    )

    for query_idx, similar_docs in similarities:
        print(f"Query {query_idx}: {len(similar_docs)} similar documents found")
        for ref_idx, score in similar_docs[:3]:  # Top 3
            print(f"  Reference {ref_idx}: {score:.3f} similarity")

# Run examples
if __name__ == "__main__":
    asyncio.run(batch_processing_example())
    asyncio.run(rag_ingestion_example())
    asyncio.run(similarity_example())
```

#### Retry Logic and Circuit Breaker

```python
from src.utils.retry_logic import (
    with_rag_retry, RAGRetryConfig, AsyncCircuitBreaker
)

# Configure retry behavior
retry_config = RAGRetryConfig(
    max_retries=3,
    initial_delay=1.0,
    backoff_multiplier=2.0,
    max_delay=30.0,
    jitter=True
)

# Apply retry logic to RAG operations
@with_rag_retry(
    config=retry_config,
    operation_name="document_retrieval"
)
async def reliable_rag_query(query: str):
    # This function will automatically retry on failures
    # with exponential backoff and circuit breaker protection
    return await async_query_rag_simple(query)

# Manual circuit breaker usage
async def circuit_breaker_example():
    circuit_breaker = AsyncCircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30.0
    )

    async def potentially_failing_operation():
        # Your potentially failing code here
        return "success"

    try:
        result = await circuit_breaker.call(potentially_failing_operation())
        print(f"Operation succeeded: {result}")
    except Exception as e:
        print(f"Operation failed or circuit breaker is open: {e}")

    # Check circuit breaker status
    stats = circuit_breaker.get_stats()
    print(f"Circuit breaker state: {circuit_breaker.state}")
    print(f"Failure count: {circuit_breaker.failure_count}")
```

## 🏗️ Architecture

### Core Components

- **`src/main.py`**: Core LLM interface with security and performance features
- **`src/rag_pipeline.py`**: Simplified RAG interface for document queries
- **`src/utils/rag_pipeline.py`**: Comprehensive RAG implementation with LangChain
- **`src/utils/vector_db.py`**: Vector database with FAISS backend
- **`src/config_loader.py`**: Configuration management and validation
- **`willow.py`**: Main orchestrator and CLI interface

### RAG Pipeline Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │ -> │  RAG Pipeline   │ -> │ Augmented LLM   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │  Vector Database    │
                    │  - FAISS Index      │
                    │  - Embeddings       │
                    │  - Metadata         │
                    └─────────────────────┘
```

## ⚙️ Configuration

### Environment Variables

```bash
# API Keys (optional - for cloud LLM providers)
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export ANTHROPIC_API_KEY="your-claude-key"

# RAG Configuration (optional)
export RAG_DB_PATH="./knowledge_base"
export RAG_CHUNK_SIZE="500"
export RAG_TOP_K="5"
```

### Configuration Files

- **`config.yaml`**: Main configuration file
- **`core_constitution.json`**: AI behavior guidelines
- **`requirements.txt`**: Core dependencies
- **`requirements-rag.txt`**: Optional RAG dependencies

## 🧪 Testing

### Run All Tests

```bash
# Run core tests
python -m pytest tests/ -v

# Run specific test suites
python tests/test_performance.py
python tests/test_security.py
python tests/test_rag_pipeline_integration.py

# Run performance benchmarks
python benchmark_performance.py
```

### Test RAG Integration

```bash
# Test basic integration
python test_vector_db_simple.py

# Full RAG demonstration
python demo_rag_integration.py
```

## 📊 Performance Features

- **Caching**: LRU caches for models, embeddings, and validation
- **Async Operations**: Non-blocking I/O and concurrent processing
- **Batch Processing**: Efficient handling of multiple queries
- **Memory Management**: Weak references and garbage collection optimization
- **Metrics Collection**: Built-in performance monitoring

## 🛡️ Security Features

- **Input Validation**: Prompt length limits and content filtering
- **Path Sanitization**: Secure file operations with path validation
- **Model Validation**: Whitelist-based model name verification
- **Error Handling**: Comprehensive exception management
- **Safe Execution**: Protection against code injection and resource exhaustion

## 🔌 Dependencies

### Core Dependencies

```
psutil>=5.9.0     # System monitoring
rich>=13.0.0      # Terminal formatting
```

### Optional RAG Dependencies

```
langchain>=0.1.0              # LLM framework
langchain-community>=0.0.10   # Community extensions
faiss-cpu>=1.7.4             # Vector database
sentence-transformers>=2.2.2  # Embeddings
datasets>=2.14.0              # Data handling
ragas>=0.1.0                  # RAG evaluation
numpy>=1.24.0                 # Numerical computing
scipy>=1.10.0                 # Scientific computing
```

## 🚧 Graceful Degradation

Willow v6 is designed to work perfectly without optional dependencies:

- **Without RAG dependencies**: Falls back to standard LLM queries
- **Without API keys**: Uses local models when available
- **Without internet**: Operates entirely offline with local models
- **Minimal setup**: Core functionality requires only 2 dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Run the test suite: `python -m pytest tests/`
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- LangChain for the RAG framework
- FAISS for efficient vector search
- Sentence Transformers for embeddings
- The open-source AI community

---

**Willow v6.0.0** - Built with ❤️ for the AI automation community
