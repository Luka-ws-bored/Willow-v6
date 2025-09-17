import subprocess
import logging
import os
import json
import shlex
import re
import asyncio
import time
from typing import Dict, List, Any, TypedDict, Optional, Union
from pathlib import Path
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import weakref

try:
    from .config_loader import get_config, load_constitution
except ImportError:
    from config_loader import get_config, load_constitution

# Enhanced logging configuration
try:
    from .utils.logging_config import get_willow_logger, log_rag_operation, rag_logger, log_missing_dependencies
except ImportError:
    try:
        from utils.logging_config import get_willow_logger, log_rag_operation, rag_logger, log_missing_dependencies
    except ImportError:
        # Fallback to standard logging
        def get_willow_logger(log_level="INFO", log_file=None):
            return logging.getLogger('willow')
        def log_rag_operation(operation, cache_hit=False):
            def decorator(func):
                return func
            return decorator
        def rag_logger():
            return logging.getLogger('willow.rag')
        def log_missing_dependencies(deps, component="RAG"):
            logging.warning(f"{component} dependencies missing: {deps}")

# Optional RAG imports - graceful degradation if not available
try:
    try:
        from .utils.rag_pipeline import get_rag_pipeline, RAGError
        from .rag_pipeline import RAGPipeline as SimpleRAGPipeline, create_rag_pipeline
    except ImportError:
        from utils.rag_pipeline import get_rag_pipeline, RAGError
        from rag_pipeline import RAGPipeline as SimpleRAGPipeline, create_rag_pipeline
    RAG_AVAILABLE = True
except ImportError:
    # RAG functionality not available - define dummy classes for type hints
    RAG_AVAILABLE = False
    class RAGError(Exception):
        pass
    async def get_rag_pipeline(*args, **kwargs):
        raise RAGError("RAG functionality not available - install langchain dependencies")
    def create_rag_pipeline(*args, **kwargs):
        raise RAGError("RAG functionality not available - install vector database dependencies")

# Performance optimization - enhanced caching and threading
_executor_pool: Optional[ThreadPoolExecutor] = None
_model_cache_lock = Lock()
_model_cache = weakref.WeakValueDictionary()
_validation_cache = {}  # Cache for model name validation
_rag_query_cache = {}  # Cache for RAG query results
_rag_cache_lock = Lock()
_rag_cache_max_size = 100
_rag_cache_ttl = 1800  # 30 minutes

# Performance monitoring with additional metrics
_perf_stats = {
    'model_queries': 0,
    'cache_hits': 0,
    'validation_hits': 0,
    'total_query_time': 0.0,
    'total_validation_time': 0.0,
    'rag_queries': 0,
    'rag_cache_hits': 0,
    'rag_query_time': 0.0,
    'rag_fallback_count': 0
}

def get_executor() -> ThreadPoolExecutor:
    """Get thread pool executor for concurrent operations."""
    global _executor_pool
    if _executor_pool is None:
        _executor_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="willow_")
    return _executor_pool

def get_performance_stats() -> Dict[str, Union[int, float]]:
    """Get comprehensive performance statistics."""
    stats = _perf_stats.copy()
    if stats['model_queries'] > 0:
        stats['avg_query_time'] = stats['total_query_time'] / stats['model_queries']
        stats['cache_hit_rate'] = stats['cache_hits'] / stats['model_queries']
    if stats.get('validation_hits', 0) > 0:
        total_validations = stats['model_queries'] + stats['validation_hits']
        stats['validation_cache_rate'] = stats['validation_hits'] / total_validations
    return stats

def timed_function(func):
    """Decorator to track function execution time with optimized logging."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            _perf_stats['total_query_time'] += execution_time
            # Conditional logging check moved outside to avoid overhead
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"{func.__name__} executed in {execution_time:.3f}s")
    return wrapper
# Security constants
# Valid models - updated from config
_VALID_MODELS = [
    'goekdenizguelmez/josiefied-qwen3:1.7b',
    'qwen3:0.6b',
    'nomic-embed-text:latest'
]

# Maximum prompt length to prevent resource exhaustion
_MAX_PROMPT_LENGTH = 50000

# Allowed characters in model names (alphanumeric, hyphens, dots, colons, slashes)
MODEL_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._:/-]+$')

@lru_cache(maxsize=1)
def get_valid_models() -> List[str]:
    """Get list of valid models from configuration (cached)."""
    return config.get_model_config()['valid_models']

@lru_cache(maxsize=1)
def get_max_prompt_length() -> int:
    """Get maximum prompt length from configuration (cached)."""
    return config.get_model_config()['max_prompt_length']

def validate_model_name(model: str) -> bool:
    """Validate model name against security criteria with caching.
    
    Args:
        model: Model name to validate
        
    Returns:
        True if model name is valid, False otherwise
    """
    if not model or not isinstance(model, str):
        return False
    
    # Check validation cache first
    if model in _validation_cache:
        _perf_stats['validation_hits'] += 1
        return _validation_cache[model]
    
    start_time = time.perf_counter()
    
    # Check if model is in our whitelist
    valid_models = get_valid_models()
    if model not in valid_models:
        logging.warning(f"Model '{model}' not in valid model list: {valid_models}")
        result = False
    # Check format to prevent injection
    elif not MODEL_NAME_PATTERN.match(model):
        logging.warning(f"Model name '{model}' contains invalid characters")
        result = False
    else:
        result = True
    
    # Cache the result
    _validation_cache[model] = result
    
    # Track timing
    _perf_stats['total_validation_time'] += time.perf_counter() - start_time
    
    return result

def validate_prompt(prompt: str) -> bool:
    """Validate prompt for security and resource constraints.
    
    Args:
        prompt: User prompt to validate
        
    Returns:
        True if prompt is valid, False otherwise
    """
    if not prompt or not isinstance(prompt, str):
        return False
    
    if len(prompt.strip()) == 0:
        return False
    
    max_length = get_max_prompt_length()
    if len(prompt) > max_length:
        logging.warning(f"Prompt too long: {len(prompt)} chars (max: {max_length})")
        return False
    
    return True

# Constitution type definitions
class IdentityDict(TypedDict):
    name: str
    version: str
    description: str

class PromptDict(TypedDict):
    name: str
    id: str
    description: str
    file: str
    usage: str

# Using a more flexible approach for the constitution structure
# since it contains a key with spaces ("Prompt Library")
ConstitutionType = Dict[str, Any]

# Initialize configuration
config = get_config()
constitution: ConstitutionType = load_constitution()
model_config = config.get_model_config()

# Get configuration values
MODEL_TIMEOUTS = model_config['model_timeouts']

# Type assertions for better type safety when accessing known keys
_identity: IdentityDict = constitution["Identity"]
_prompt_library: List[PromptDict] = constitution["Prompt Library"]

print("Willow's Core Constitution loaded successfully!")

@lru_cache(maxsize=1)
@timed_function
def _get_model_priority() -> List[str]:
    """Get model priority list with security validation (cached).
    
    Returns:
        List of validated model names
    """
    # Get models from config
    models = get_valid_models()
    
    # Validate all models efficiently using list comprehension
    validated_models = [model for model in models if validate_model_name(model)]
    
    if len(validated_models) != len(models):
        invalid_models = set(models) - set(validated_models)
        logging.error(f"Invalid models in priority list: {invalid_models}")
    
    return validated_models

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.get_log_level()),
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Function to list available Ollama models
@lru_cache(maxsize=1, typed=True)
@timed_function
def list_available_models() -> List[str]:
    """Get a list of available Ollama models safely (cached).
    
    Returns:
        List of validated model names
        
    Raises:
        subprocess.CalledProcessError: If ollama command fails
        subprocess.TimeoutExpired: If command times out
    """
    try:
        # Use safe subprocess call with timeout
        result = subprocess.run(
            ["ollama", "list"],  # Safe: using list, no shell=True
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace',
            timeout=30  # Prevent hanging
        )
        
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        
        # Use generator expression and list comprehension for efficiency
        models = [
            line.split()[0] for line in lines 
            if line.strip() and validate_model_name(line.split()[0])
        ]
        
        # Log skipped models efficiently
        all_model_names = [line.split()[0] for line in lines if line.strip()]
        skipped_models = set(all_model_names) - set(models)
        if skipped_models:
            logging.warning(f"Skipping invalid model names: {skipped_models}")
        
        return models
        
    except subprocess.TimeoutExpired:
        logging.error("Ollama list command timed out after 30 seconds")
        return []
    except subprocess.CalledProcessError as e:
        logging.error(f"Ollama list failed: {e.stderr if e.stderr else str(e)}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error listing models: {str(e)}")
        return []

@timed_function
def query_llm(prompt: str, model: Optional[str] = None, models: Optional[List[str]] = None) -> str:
    """Query local LLMs in priority order with proper timeout and fallback.

    Args:
        prompt: User prompt to send to the model
        model: Single model to use (overrides models list)
        models: Optional list to override default priority
        
    Returns:
        Model output (first successful) or descriptive error string
        
    Raises:
        ValueError: If prompt or model parameters are invalid
    """
    _perf_stats['model_queries'] += 1
    
    # Validate inputs
    if not validate_prompt(prompt):
        raise ValueError("Invalid prompt: must be non-empty string under 50000 characters")
    
    if model:
        if not validate_model_name(model):
            raise ValueError(f"Invalid model name: {model}")
        models = [model]
    else:
        models = models or _get_model_priority()
        
        # Validate all models in the list efficiently
        validated_models = [m for m in models if validate_model_name(m)]
        
        if len(validated_models) != len(models):
            invalid_models = set(models) - set(validated_models)
            logging.warning(f"Skipping invalid models in list: {invalid_models}")
        
        models = validated_models
        
        if not models:
            raise ValueError("No valid models available")

    # Try each model with optimized error collection
    errors = []
    logger = logging.getLogger()
    is_debug = logger.isEnabledFor(logging.DEBUG)
    
    for current_model in models:
        timeout = MODEL_TIMEOUTS.get(current_model, MODEL_TIMEOUTS['default'])
        
        # Only log for debug or long-running models to reduce logging overhead
        if timeout >= 60 or is_debug:
            logging.info(f"Trying model: {current_model} with timeout={timeout}s")
            if timeout >= 60:
                logging.info('⏳ Model still processing... this may take up to %ds' % timeout)

        try:
            # Safe subprocess call: using list args, no shell=True, validated inputs
            proc = subprocess.run(
                ['ollama', 'run', current_model, prompt],  # Safe: parameterized list
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
                encoding='utf-8',
                errors='replace'
            )

            output = (proc.stdout or '').strip()
            if output:
                if is_debug:
                    logging.info(f"Model {current_model} returned output (length {len(output)}).")
                return output
            else:
                error_msg = f"Model {current_model} returned empty output"
                errors.append(error_msg)
                logging.warning(f"{error_msg}; trying next model.")
                continue

        except subprocess.TimeoutExpired as te:
            error_msg = f"Timeout with {current_model}: {str(te)}"
            errors.append(error_msg)
            logging.warning(f"{error_msg} -- trying next model.")
            continue

        except subprocess.CalledProcessError as cpe:
            stderr = cpe.stderr.strip() if cpe.stderr else ''
            error_msg = f"Model {current_model} failed (CalledProcessError): {stderr}"
            errors.append(error_msg)
            logging.warning(f"{error_msg} -- trying next model.")
            continue

        except Exception as e:
            error_msg = f"Unexpected error while calling model {current_model}: {str(e)}"
            errors.append(error_msg)
            logging.error(f"{error_msg} -- trying next model.")
            continue

    # If loop completes, all models failed - create efficient error message using join
    recent_errors = errors[-3:]  # Last 3 errors
    error_lines = [f"  - {error}" for error in recent_errors]
    error_summary = '\n'.join(error_lines)
    err = '\n'.join([
        "Error: All configured models failed or timed out. Recent errors:",
        error_summary,
        "Check Ollama, model availability, and system resources."
    ])
    logging.error(err)
    return err

async def async_query_llm(
    prompt: str, 
    model: Optional[str] = None, 
    models: Optional[List[str]] = None
) -> str:
    """Asynchronous version of query_llm for better concurrency.
    
    Args:
        prompt: User prompt to send to the model
        model: Single model to use (overrides models list)
        models: Optional list to override default priority
        
    Returns:
        Model output (first successful) or descriptive error string
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(get_executor(), query_llm, prompt, model, models)

def batch_query_llm(prompts: List[str], model: Optional[str] = None, max_workers: Optional[int] = None) -> List[str]:
    """Process multiple prompts concurrently for better throughput.
    
    Args:
        prompts: List of prompts to process
        model: Model to use for all prompts
        max_workers: Maximum number of concurrent workers (auto-sized if None)
        
    Returns:
        List of responses in the same order as prompts
    """
    if not prompts:
        return []
    
    # Auto-size workers based on prompt count and system resources
    if max_workers is None:
        max_workers = min(len(prompts), 3, os.cpu_count() or 1)
    
    # Use ThreadPoolExecutor for concurrent processing
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="willow_batch_") as executor:
        futures = [executor.submit(query_llm, prompt, model) for prompt in prompts]
        results = [future.result() for future in futures]
    
    return results

def clear_caches() -> None:
    """Clear all function caches, validation cache, and RAG cache to free memory."""
    global _validation_cache, _rag_query_cache
    
    list_available_models.cache_clear()
    _get_model_priority.cache_clear()
    get_valid_models.cache_clear()
    get_max_prompt_length.cache_clear()
    
    with _model_cache_lock:
        _validation_cache.clear()
    
    with _rag_cache_lock:
        _rag_query_cache.clear()
    
    logging.info("All performance caches cleared including RAG query cache")


def _get_rag_cache_key(prompt: str, documents: Optional[List[str]] = None, docs_path: Optional[str] = None, top_k: int = 5) -> str:
    """Generate cache key for RAG queries."""
    import hashlib
    import json
    
    cache_data = {
        'prompt': prompt.strip().lower(),
        'documents': documents if documents else None,
        'docs_path': str(docs_path) if docs_path else None,
        'top_k': top_k
    }
    
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


def _get_rag_cached_result(cache_key: str) -> Optional[str]:
    """Get cached RAG result if available and not expired."""
    with _rag_cache_lock:
        if cache_key in _rag_query_cache:
            result, timestamp = _rag_query_cache[cache_key]
            if time.time() - timestamp < _rag_cache_ttl:
                _perf_stats['rag_cache_hits'] += 1
                return result
            else:
                # Remove expired entry
                del _rag_query_cache[cache_key]
    return None


def _cache_rag_result(cache_key: str, result: str):
    """Cache RAG query result with TTL."""
    with _rag_cache_lock:
        # Implement LRU eviction if cache is full
        if len(_rag_query_cache) >= _rag_cache_max_size:
            # Remove oldest entry
            oldest_key = min(_rag_query_cache.keys(), 
                            key=lambda k: _rag_query_cache[k][1])
            del _rag_query_cache[oldest_key]
        
        _rag_query_cache[cache_key] = (result, time.time())

def warm_up_models() -> None:
    """Pre-warm model availability cache for better first-run performance."""
    try:
        # Use batch operations for warming up
        available_models = list_available_models()
        priority_models = _get_model_priority()
        
        # Pre-validate common model names to cache validation results
        common_models = available_models[:5]  # Top 5 most likely to be used
        for model in common_models:
            validate_model_name(model)  # Warms up validation cache
        
        logging.info(f"Model caches warmed up: {len(available_models)} available, {len(priority_models)} priority")
    except Exception as e:
        logging.warning(f"Failed to warm up model caches: {e}")

async def async_query_rag(prompt: str, docs_path: Optional[Union[str, Path]] = None) -> str:
    """Query the RAG pipeline with augmented document retrieval.
    
    Args:
        prompt: User prompt for RAG-enhanced query
        docs_path: Optional path to documents (uses default if None)
        
    Returns:
        RAG-augmented response or error message
        
    Raises:
        ValueError: If prompt is invalid
    """
    # Check if RAG is available
    if not RAG_AVAILABLE:
        logging.warning("RAG functionality not available - falling back to standard LLM")
        return await async_query_llm(prompt)
    
    # Validate prompt using existing security functions
    if not validate_prompt(prompt):
        raise ValueError("Invalid prompt: must be non-empty string under 50000 characters")
    
    try:
        # Get RAG pipeline instance
        rag_pipeline = await get_rag_pipeline(docs_path)
        
        # Retrieve relevant context
        context = await rag_pipeline.get_context_for_query(prompt)
        
        if not context:
            logging.warning("No relevant context found for RAG query")
            # Fallback to standard LLM query
            return await async_query_llm(prompt)
        
        # Create augmented prompt with context
        augmented_prompt = f"""Context from relevant documents:
{context}

User Question: {prompt}

Please answer the question based on the provided context. If the context doesn't contain relevant information, clearly state that and provide a general response."""
        
        # Use async LLM query with the augmented prompt
        response = await async_query_llm(augmented_prompt)
        
        # Log successful RAG query (debug level to avoid spam)
        logging.debug(f"RAG query completed successfully (prompt length: {len(prompt)}, context length: {len(context)})")
        
        return response
        
    except RAGError as e:
        logging.error(f"RAG pipeline error: {e}")
        # Fallback to standard LLM query
        logging.info("Falling back to standard LLM query")
        return await async_query_llm(prompt)
        
    except Exception as e:
        logging.error(f"Unexpected error in RAG query: {e}")
        # Fallback to standard LLM query
        return await async_query_llm(prompt)

async def batch_query_rag(
    prompts: List[str], 
    docs_path: Optional[Union[str, Path]] = None, 
    max_workers: Optional[int] = None
) -> List[str]:
    """Process multiple prompts with RAG enhancement concurrently.
    
    Args:
        prompts: List of prompts to process
        docs_path: Optional path to documents
        max_workers: Maximum number of concurrent workers
        
    Returns:
        List of RAG-augmented responses
    """
    if not prompts:
        return []
    
    # Auto-size workers for RAG queries (more conservative than standard LLM)
    if max_workers is None:
        max_workers = min(len(prompts), 2, os.cpu_count() or 1)
    
    # Process all prompts concurrently
    tasks = [async_query_rag(prompt, docs_path) for prompt in prompts]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error messages
    processed_responses = []
    for i, response in enumerate(responses):
        if isinstance(response, Exception):
            error_msg = f"Error processing prompt {i+1}: {str(response)}"
            logging.error(error_msg)
            processed_responses.append(error_msg)
        else:
            processed_responses.append(response)
    
@log_rag_operation('simple_rag_query')
async def async_query_rag_simple(
    prompt: str, 
    documents: Optional[List[str]] = None,
    docs_path: Optional[Union[str, Path]] = None,
    top_k: int = 5
) -> str:
    """Query using the simplified RAG pipeline with direct document input.
    
    Args:
        prompt: User prompt for RAG-enhanced query
        documents: Optional list of documents to use for context
        docs_path: Optional path to vector database (if documents not provided)
        top_k: Number of documents to retrieve
        
    Returns:
        RAG-augmented response or error message
        
    Raises:
        ValueError: If prompt is invalid
    """
    rag_log = rag_logger()
    start_time = time.perf_counter()
    
    # Check if RAG is available
    if not RAG_AVAILABLE:
        missing_deps = ["langchain", "langchain-community", "faiss-cpu", "sentence-transformers"]
        log_missing_dependencies(missing_deps, "RAG")
        rag_log.warning("RAG functionality not available - falling back to standard LLM")
        return await async_query_llm(prompt)
    
    # Validate prompt using existing security functions
    if not validate_prompt(prompt):
        rag_log.error(f"Invalid prompt validation failed: length={len(prompt) if prompt else 0}")
        raise ValueError("Invalid prompt: must be non-empty string under 50000 characters")
    
    rag_log.info(f"Starting simple RAG query: prompt_length={len(prompt)}, documents_provided={bool(documents)}, top_k={top_k}")
    
    # Check cache first
    cache_key = _get_rag_cache_key(prompt, documents, str(docs_path) if docs_path else None, top_k)
    cached_result = _get_rag_cached_result(cache_key)
    if cached_result is not None:
        total_time = time.perf_counter() - start_time
        rag_log.info(
            "Simple RAG query served from cache",
            extra={
                'rag_operation': 'cache_hit',
                'duration': total_time,
                'cache_hit': True
            }
        )
        return cached_result
    
    try:
        context_start_time = time.perf_counter()
        
        if documents:
            # Use quick RAG query with provided documents
            from rag_pipeline import quick_rag_query
            rag_log.debug(f"Using quick RAG with {len(documents)} documents")
            context_result = await quick_rag_query(prompt, documents, top_k=top_k)
        else:
            # Use persistent RAG pipeline
            rag_log.debug(f"Using persistent RAG pipeline: db_path={docs_path}")
            rag = create_rag_pipeline(db_path=docs_path)
            context_result = await rag.query_with_context_async(prompt, top_k=top_k)
        
        context_time = time.perf_counter() - context_start_time
        rag_log.info(
            f"Context retrieval completed", 
            extra={
                'rag_operation': 'retrieval',
                'duration': context_time,
                'documents_found': len(context_result['documents']),
                'cache_hit': context_time < 0.1  # Assume cache if very fast
            }
        )
        
        if not context_result['documents']:
            rag_log.warning("No relevant context found for RAG query - falling back to standard LLM")
            # Fallback to standard LLM query
            return await async_query_llm(prompt)
        
        # Use the formatted context directly
        augmented_prompt = context_result['context']
        rag_log.debug(f"Generated augmented prompt: {len(augmented_prompt)} characters")
        
        # Use async LLM query with the augmented prompt
        llm_start_time = time.perf_counter()
        response = await async_query_llm(augmented_prompt)
        llm_time = time.perf_counter() - llm_start_time
        
        total_time = time.perf_counter() - start_time
        
        # Log successful RAG query with performance metrics
        rag_log.info(
            f"Simple RAG query completed successfully",
            extra={
                'rag_operation': 'query',
                'duration': total_time,
                'context_retrieval_time': context_time,
                'llm_generation_time': llm_time,
                'documents_used': len(context_result['documents']),
                'response_length': len(response)
            }
        )
        
        # Cache the successful result
        _cache_rag_result(cache_key, response)
        _perf_stats['rag_queries'] += 1
        _perf_stats['rag_query_time'] += total_time
        
        return response
        
    except RAGError as e:
        error_time = time.perf_counter() - start_time
        rag_log.error(
            f"RAG pipeline error: {e}",
            extra={
                'rag_operation': 'error',
                'duration': error_time,
                'error_type': 'RAGError'
            }
        )
        # Fallback to standard LLM query
        rag_log.info("Falling back to standard LLM query due to RAG error")
        _perf_stats['rag_fallback_count'] += 1
        return await async_query_llm(prompt)
        
    except Exception as e:
        error_time = time.perf_counter() - start_time
        rag_log.error(
            f"Unexpected error in simple RAG query: {e}",
            extra={
                'rag_operation': 'error',
                'duration': error_time,
                'error_type': type(e).__name__
            }
        )
        # Fallback to standard LLM query
        _perf_stats['rag_fallback_count'] += 1
        return await async_query_llm(prompt)

# Export for imports with performance functions
__all__ = [
    'query_llm', 
    'async_query_llm',
    'batch_query_llm',
    'async_query_rag',
    'batch_query_rag',
    'async_query_rag_simple',
    'list_available_models',
    'validate_model_name',
    'validate_prompt',
    'get_performance_stats',
    'clear_caches',
    'warm_up_models'
]

# Optional: small local self-test when run directly
if __name__ == '__main__':
    # Show available models
    available_models = list_available_models()
    print(f"Available models: {', '.join(available_models) if available_models else 'None'}")
    
    test_prompt = "Hello Willow, briefly introduce yourself in two friendly sentences."
    print("\nAttempting to connect with fallback chain...")
    response = query_llm(test_prompt)
    print("\nWillow Response:")
    print(response)
    print("\n🌲 Willow is ready!")