# RAG Pipeline Documentation

## Overview

The Retrieval-Augmented Generation (RAG) pipeline in Willow v6 enables the system to answer queries by retrieving relevant information from document collections and augmenting responses with contextual information. This implementation leverages LangChain for document processing, FAISS for vector storage, and includes RAGAS evaluation for quality assessment.

## Features

- **Secure Document Loading**: Path validation and safe file operations
- **Async Processing**: Full async/await support for better performance
- **Performance Monitoring**: Comprehensive metrics and caching
- **RAGAS Evaluation**: Quality assessment with faithfulness and relevance metrics
- **Hallucination Detection**: Simple overlap-based detection system
- **Batch Processing**: Efficient handling of multiple queries
- **Health Monitoring**: System status and diagnostic capabilities

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query    │ -> │  RAG Pipeline   │ -> │ Augmented LLM   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                               │
                               v
                    ┌─────────────────────┐
                    │  Document Storage   │
                    │  - Text Files       │
                    │  - Vector Store     │
                    │  - Embeddings       │
                    └─────────────────────┘
```

## Quick Start

### Basic Usage

```python
import asyncio
from src.main import async_query_rag

async def main():
    # Simple RAG query
    response = await async_query_rag("What is Python programming?")
    print(response)

# Run async function
asyncio.run(main())
```

### Batch Processing

```python
import asyncio
from src.main import batch_query_rag

async def main():
    prompts = [
        "What is machine learning?",
        "How does web development work?",
        "Explain artificial intelligence"
    ]

    responses = await batch_query_rag(prompts)
    for i, response in enumerate(responses):
        print(f"Query {i+1}: {response}")

asyncio.run(main())
```

### Advanced RAG Pipeline Usage

```python
import asyncio
from pathlib import Path
from src.utils.rag_pipeline import RAGPipeline, RAGASEvaluator

async def advanced_example():
    # Initialize RAG pipeline
    docs_path = Path("./docs")
    rag_pipeline = RAGPipeline(
        docs_path=docs_path,
        chunk_size=500,
        chunk_overlap=50,
        retrieval_k=5
    )

    # Initialize vector store
    await rag_pipeline.initialize_vector_store()

    # Query for context
    query = "How do I configure the system?"
    context = await rag_pipeline.get_context_for_query(query)
    print(f"Retrieved context: {context}")

    # Get documents with similarity scores
    docs_with_scores = await rag_pipeline.search_documents(query, k=3)
    for doc, score in docs_with_scores:
        print(f"Score: {score:.3f}, Content: {doc.page_content[:100]}...")

    # Health check
    health = await rag_pipeline.health_check()
    print(f"Pipeline health: {health}")

    # Performance metrics
    metrics = rag_pipeline.metrics.get_summary()
    print(f"Performance metrics: {metrics}")

asyncio.run(advanced_example())
```

## Configuration

### Environment Variables

```bash
# Optional: Custom embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: Custom chunk settings
RAG_CHUNK_SIZE=500
RAG_CHUNK_OVERLAP=50
RAG_RETRIEVAL_K=5
```

### Programmatic Configuration

```python
from src.utils.rag_pipeline import RAGPipeline

# Custom configuration
rag_pipeline = RAGPipeline(
    docs_path="./my_documents",
    chunk_size=300,          # Smaller chunks for more precise retrieval
    chunk_overlap=30,        # 10% overlap
    retrieval_k=3,          # Return top 3 most relevant documents
    embedding_model="sentence-transformers/all-mpnet-base-v2"  # Better but slower
)
```

## Document Management

### Supported File Types

- Text files (`.txt`)
- Markdown files (`.md`)
- Extensible through LangChain loaders

### Document Structure

```
docs/
├── user_guides/
│   ├── getting_started.txt
│   └── advanced_features.txt
├── api_reference/
│   ├── authentication.md
│   └── endpoints.md
└── troubleshooting/
    └── common_issues.txt
```

### Loading Documents

```python
from src.utils.rag_pipeline import SecureDocumentLoader
from pathlib import Path

# Initialize loader
loader = SecureDocumentLoader(project_root=Path("."))

# Load single document
documents = loader.load_document("./docs/guide.txt")

# Load entire directory
all_docs = loader.load_directory("./docs", glob_pattern="**/*.txt")
```

## Evaluation and Quality Assessment

### RAGAS Evaluation

```python
import asyncio
from src.utils.rag_pipeline import RAGASEvaluator, RAGPipeline

async def evaluate_quality():
    # Setup
    rag_pipeline = RAGPipeline("./docs")
    evaluator = RAGASEvaluator(rag_pipeline)

    # Single evaluation
    scores = await evaluator.evaluate_response(
        question="What is the installation process?",
        answer="To install, run pip install willow",
        contexts=["Installation guide: Use pip install willow to get started"],
        ground_truth="Run pip install willow"  # Optional
    )

    print(f"Evaluation scores: {scores}")
    # Output: {'faithfulness': 0.85, 'answer_relevancy': 0.90, 'context_precision': 0.78}

    # Batch evaluation
    evaluation_data = [
        {
            "question": "How to install?",
            "answer": "Use pip install",
            "contexts": ["Installation: pip install willow"],
            "ground_truth": "pip install willow"
        },
        # ... more evaluations
    ]

    batch_results = await evaluator.batch_evaluate(evaluation_data)
    print(f"Batch results: {batch_results}")

asyncio.run(evaluate_quality())
```

### Hallucination Detection

```python
from src.utils.rag_pipeline import RAGASEvaluator

evaluator = RAGASEvaluator(None)  # No pipeline needed for this function

# Check for hallucination
result = evaluator.detect_hallucination(
    answer="Python is a programming language created in 1991",
    contexts=["Python is a high-level programming language created by Guido van Rossum"],
    threshold=0.7
)

print(f"Hallucination risk: {result['hallucination_risk']}")
print(f"Confidence: {result['confidence']}")
```

## Performance Optimization

### Caching

The RAG pipeline includes multiple levels of caching:

- **Document Cache**: Recently retrieved documents
- **Embedding Cache**: Model embeddings stored locally
- **Validation Cache**: Model name validation results

```python
# Clear caches when needed
rag_pipeline.clear_cache()

# Check cache effectiveness
metrics = rag_pipeline.metrics.get_summary()
cache_hit_rate = metrics.get('cache_hit_rate', 0)
print(f"Cache hit rate: {cache_hit_rate:.1%}")
```

### Async Processing

All RAG operations support async/await for better performance:

```python
import asyncio

async def concurrent_queries():
    # Process multiple queries concurrently
    tasks = [
        async_query_rag("Query 1"),
        async_query_rag("Query 2"),
        async_query_rag("Query 3")
    ]

    results = await asyncio.gather(*tasks)
    return results
```

### Performance Monitoring

```python
# Get comprehensive performance metrics
metrics = rag_pipeline.metrics.get_summary()

print(f"Average retrieval time: {metrics.get('avg_retrieval_time', 0):.3f}s")
print(f"Average generation time: {metrics.get('avg_generation_time', 0):.3f}s")
print(f"Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")
print(f"Total queries processed: {metrics.get('total_queries', 0)}")
```

## Error Handling

### Common Errors and Solutions

```python
from src.utils.rag_pipeline import RAGError

try:
    response = await async_query_rag("My query")
except RAGError as e:
    print(f"RAG-specific error: {e}")
    # Fallback to standard LLM
    response = await async_query_llm("My query")
except ValueError as e:
    print(f"Invalid input: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Graceful Degradation

The system automatically falls back to standard LLM queries when RAG fails:

```python
# This will automatically fallback if RAG fails
response = await async_query_rag("Query with fallback")
```

## Security Considerations

### Path Validation

All document paths are validated through the secure file operations system:

```python
# Automatic security validation
from src.utils.rag_pipeline import SecureDocumentLoader

loader = SecureDocumentLoader(project_root=Path("."))
# Only files within project_root can be accessed
# Path traversal attacks are prevented
```

### Input Validation

```python
# Prompt validation (same as standard LLM)
if not validate_prompt(user_input):
    raise ValueError("Invalid prompt")
```

## Troubleshooting

### Common Issues

#### RAG Pipeline Initialization Fails

```python
# Check dependencies
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.vectorstores import FAISS
    print("✅ LangChain dependencies available")
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Run: pip install langchain langchain-community faiss-cpu sentence-transformers")
```

#### No Documents Retrieved

```python
# Check document availability
health = await rag_pipeline.health_check()
if not health['docs_path_exists']:
    print("❌ Documents directory not found")
elif health['document_count'] == 0:
    print("❌ No documents loaded")
else:
    print(f"✅ {health['document_count']} documents available")
```

#### Poor Retrieval Quality

```python
# Adjust retrieval parameters
rag_pipeline = RAGPipeline(
    docs_path="./docs",
    chunk_size=200,          # Smaller chunks for more precise retrieval
    chunk_overlap=40,        # More overlap for better context
    retrieval_k=10,          # Retrieve more documents
    embedding_model="sentence-transformers/all-mpnet-base-v2"  # Better embeddings
)
```

#### RAGAS Evaluation Not Working

```python
# Check RAGAS availability
from src.utils.rag_pipeline import RAGAS_AVAILABLE

if not RAGAS_AVAILABLE:
    print("❌ RAGAS not available")
    print("Run: pip install ragas datasets")
else:
    print("✅ RAGAS evaluation available")
```

### Performance Issues

#### Slow Initialization

```python
# Use smaller embedding models for faster startup
rag_pipeline = RAGPipeline(
    docs_path="./docs",
    embedding_model="sentence-transformers/all-MiniLM-L6-v2"  # Faster, smaller model
)
```

#### High Memory Usage

```python
# Reduce chunk size and retrieval count
rag_pipeline = RAGPipeline(
    docs_path="./docs",
    chunk_size=300,    # Smaller chunks
    retrieval_k=3      # Fewer retrieved documents
)
```

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
python -m pytest tests/test_rag_pipeline.py -v
```

### Performance Benchmarks

```bash
python benchmark_performance.py
```

### Integration Tests

```python
import asyncio
from src.main import async_query_rag

async def integration_test():
    try:
        response = await async_query_rag("Test query")
        print("✅ RAG integration working")
        return True
    except Exception as e:
        print(f"❌ RAG integration failed: {e}")
        return False

asyncio.run(integration_test())
```

## API Reference

### Main Functions

#### `async_query_rag(prompt: str, docs_path: Optional[Path] = None) -> str`

Query the RAG pipeline with document augmentation.

**Parameters:**

- `prompt`: User query string
- `docs_path`: Optional path to documents directory

**Returns:** Augmented response string

**Raises:** `ValueError` for invalid prompts, `RAGError` for pipeline issues

#### `batch_query_rag(prompts: List[str], docs_path: Optional[Path] = None, max_workers: Optional[int] = None) -> List[str]`

Process multiple prompts with RAG enhancement.

**Parameters:**

- `prompts`: List of query strings
- `docs_path`: Optional path to documents directory
- `max_workers`: Maximum concurrent workers

**Returns:** List of response strings

### RAGPipeline Class

#### `__init__(docs_path, chunk_size=500, chunk_overlap=50, retrieval_k=5, embedding_model="sentence-transformers/all-MiniLM-L6-v2")`

Initialize RAG pipeline.

#### `async initialize_vector_store(force_rebuild: bool = False) -> None`

Initialize or rebuild the vector store.

#### `async retrieve_documents(query: str) -> List[Document]`

Retrieve relevant documents for a query.

#### `async get_context_for_query(query: str) -> str`

Get formatted context string for a query.

#### `async health_check() -> Dict[str, Any]`

Perform comprehensive health check.

### RAGASEvaluator Class

#### `async evaluate_response(question: str, answer: str, contexts: List[str], ground_truth: Optional[str] = None) -> Dict[str, float]`

Evaluate a single response using RAGAS metrics.

#### `detect_hallucination(answer: str, contexts: List[str], threshold: float = 0.7) -> Dict[str, Any]`

Detect potential hallucinations based on context overlap.

## Best Practices

1. **Document Organization**: Structure documents logically and use descriptive filenames
2. **Chunk Size Tuning**: Balance precision (smaller chunks) vs context (larger chunks)
3. **Cache Management**: Monitor cache hit rates and clear when appropriate
4. **Error Handling**: Always implement fallback mechanisms
5. **Performance Monitoring**: Track metrics and optimize based on usage patterns
6. **Security**: Validate all inputs and use secure file operations
7. **Testing**: Include both unit tests and integration tests in your workflow

## Examples

See the `examples/` directory for complete working examples:

- `basic_rag_usage.py`: Simple RAG queries
- `batch_processing.py`: Concurrent query processing
- `evaluation_examples.py`: Quality assessment workflows
- `custom_configuration.py`: Advanced configuration options
