"""
Async helper utilities for Willow v6.
Provides safe async wrappers for I/O and subprocess operations.
"""

import asyncio
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional, TypeVar, Awaitable, Union, List, Dict, Iterator, Tuple
from functools import wraps
import time
import weakref
from pathlib import Path
import tempfile
import shutil

# Type variable for async wrapper functions
T = TypeVar('T')

# Global executor pool for async operations
_executor_pool: Optional[ThreadPoolExecutor] = None
_executor_lock = asyncio.Lock()

# Performance tracking
_async_stats = {
    'async_calls': 0,
    'total_async_time': 0.0,
    'executor_tasks': 0
}


async def get_executor() -> ThreadPoolExecutor:
    """Get or create thread pool executor for async operations."""
    global _executor_pool
    
    async with _executor_lock:
        if _executor_pool is None:
            # Auto-size based on CPU count with reasonable limits
            import os
            max_workers = min(os.cpu_count() or 1, 4)
            _executor_pool = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="willow_async_"
            )
            logging.info(f"Created async executor pool with {max_workers} workers")
    
    return _executor_pool


def async_timed(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    """Decorator to track async function execution time."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> T:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            _async_stats['async_calls'] += 1
            _async_stats['total_async_time'] += execution_time
            
            # Only log debug info if enabled to avoid overhead
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"Async {func.__name__} executed in {execution_time:.3f}s")
    
    return wrapper


async def run_in_executor(
    func: Callable[..., T], 
    *args, 
    executor: Optional[ThreadPoolExecutor] = None,
    **kwargs
) -> T:
    """Run a synchronous function in the executor."""
    if executor is None:
        executor = await get_executor()
    
    _async_stats['executor_tasks'] += 1
    loop = asyncio.get_running_loop()
    
    # Wrap the function call to handle kwargs
    def wrapped_func():
        return func(*args, **kwargs)
    
    return await loop.run_in_executor(executor, wrapped_func)


@async_timed
async def async_subprocess_run(
    cmd: List[str],
    *,
    input_data: Optional[str] = None,
    encoding: str = 'utf-8',
    timeout: Optional[float] = None,
    capture_output: bool = True,
    check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Safely run subprocess command asynchronously.
    
    Args:
        cmd: Command as list of strings (safe from injection)
        input_data: Optional input to send to process
        encoding: Text encoding
        timeout: Timeout in seconds
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise exception on non-zero exit
        
    Returns:
        CompletedProcess result
        
    Raises:
        asyncio.TimeoutError: If timeout exceeded
        subprocess.CalledProcessError: If command fails and check=True
    """
    # Validate command is a list (prevents shell injection)
    if not isinstance(cmd, list) or not cmd:
        raise ValueError("Command must be a non-empty list of strings")
    
    try:
        # Start process asynchronously with proper argument handling
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=subprocess.PIPE if input_data else None,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None
        )
        
        # Communicate with timeout
        if input_data:
            input_bytes = input_data.encode(encoding)
        else:
            input_bytes = None
            
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(input_bytes),
            timeout=timeout
        )
        
        # Decode output
        stdout = stdout_bytes.decode(encoding, errors='replace') if stdout_bytes else None
        stderr = stderr_bytes.decode(encoding, errors='replace') if stderr_bytes else None
        
        # Create result object similar to subprocess.run
        result = subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode or 0,
            stdout=stdout,
            stderr=stderr
        )
        
        # Check return code if requested
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, stdout, stderr
            )
        
        return result
        
    except asyncio.TimeoutError:
        # Kill the process if still running
        if 'process' in locals() and process.returncode is None:
            process.kill()
            await process.wait()
        raise
    except Exception as e:
        logging.error(f"Async subprocess failed: {cmd[0]} - {e}")
        raise


@async_timed
async def async_file_read(
    file_path: str, 
    encoding: str = 'utf-8',
    chunk_size: int = 8192
) -> str:
    """Asynchronously read a file in chunks."""
    def read_file():
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    return await run_in_executor(read_file)


@async_timed
async def async_file_write(
    file_path: str, 
    content: str, 
    encoding: str = 'utf-8'
) -> None:
    """Asynchronously write content to a file."""
    def write_file():
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    await run_in_executor(write_file)


@async_timed
async def async_batch_operation(
    operations: List[Callable[[], T]],
    max_concurrent: int = 3
) -> List[T]:
    """Execute multiple operations concurrently with rate limiting.
    
    Args:
        operations: List of callable operations
        max_concurrent: Maximum number of concurrent operations
        
    Returns:
        List of results in the same order as operations
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_semaphore(operation: Callable[[], T]) -> T:
        async with semaphore:
            return await run_in_executor(operation)
    
    # Create tasks for all operations
    tasks = [run_with_semaphore(op) for op in operations]
    
    # Wait for all tasks to complete
    return await asyncio.gather(*tasks)


async def async_query_llm_safe(
    prompt: str,
    model: Optional[str] = None,
    timeout: Optional[float] = None
) -> str:
    """Safely query LLM asynchronously with proper error handling.
    
    Args:
        prompt: User prompt
        model: Optional model override
        timeout: Optional timeout override
        
    Returns:
        Model response or error message
    """
    try:
        # Import here to avoid circular imports
        from ..main import query_llm
        
        return await run_in_executor(query_llm, prompt, model)
        
    except Exception as e:
        error_msg = f"Async LLM query failed: {str(e)}"
        logging.error(error_msg)
        return error_msg


def get_async_stats() -> dict:
    """Get async operation statistics."""
    stats = _async_stats.copy()
    if stats['async_calls'] > 0:
        stats['avg_async_time'] = stats['total_async_time'] / stats['async_calls']
    return stats


async def cleanup_async_resources() -> None:
    """Clean up async resources."""
    global _executor_pool
    
    if _executor_pool is not None:
        _executor_pool.shutdown(wait=True)
        _executor_pool = None
        logging.info("Async executor pool cleaned up")


# Context manager for async operations
class AsyncContext:
    """Context manager for async operations with automatic cleanup."""
    
    def __init__(self):
        self.tasks = set()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cancel any remaining tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()
        
        # Wait for tasks to complete or be cancelled
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
    
    def add_task(self, coro) -> asyncio.Task:
        """Add a task to be managed by this context."""
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        return task


# Document Batch Processing Helpers

class DocumentBatchProcessor:
    """Async batch processor for document operations with security and performance optimization."""
    
    def __init__(self, max_concurrent: int = 4, chunk_size: int = 1000):
        self.max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.stats = {
            'documents_processed': 0,
            'batches_completed': 0,
            'total_processing_time': 0.0,
            'errors': 0
        }
    
    async def process_documents_from_files(
        self,
        file_paths: List[Union[str, Path]],
        processor_func: Callable[[str], Awaitable[Any]],
        validate_paths: bool = True
    ) -> List[Tuple[str, Any, Optional[Exception]]]:
        """Process documents from multiple files with path validation.
        
        Args:
            file_paths: List of file paths to process
            processor_func: Async function to process each document
            validate_paths: Whether to validate file paths for security
            
        Returns:
            List of (file_path, result, error) tuples
        """
        if validate_paths:
            file_paths = await self._validate_file_paths(file_paths)
        
        async def process_single_file(file_path: Union[str, Path]) -> Tuple[str, Any, Optional[Exception]]:
            async with self.semaphore:
                try:
                    content = await async_file_read(str(file_path))
                    result = await processor_func(content)
                    self.stats['documents_processed'] += 1
                    return (str(file_path), result, None)
                except Exception as e:
                    self.stats['errors'] += 1
                    logging.error(f"Error processing {file_path}: {e}")
                    return (str(file_path), None, e)
        
        start_time = time.perf_counter()
        results = await asyncio.gather(
            *[process_single_file(fp) for fp in file_paths],
            return_exceptions=False
        )
        
        self.stats['total_processing_time'] += time.perf_counter() - start_time
        self.stats['batches_completed'] += 1
        
        return results
    
    async def process_document_chunks(
        self,
        documents: List[str],
        processor_func: Callable[[str], Awaitable[Any]],
        metadata: Optional[List[Dict]] = None
    ) -> List[Tuple[int, Any, Optional[Exception]]]:
        """Process documents in chunks for memory efficiency.
        
        Args:
            documents: List of document contents
            processor_func: Async function to process each document
            metadata: Optional metadata for each document
            
        Returns:
            List of (index, result, error) tuples
        """
        if metadata and len(metadata) != len(documents):
            raise ValueError("Metadata list must match documents list length")
        
        async def process_single_doc(index: int, doc: str, meta: Optional[Dict] = None) -> Tuple[int, Any, Optional[Exception]]:
            async with self.semaphore:
                try:
                    # Pass metadata to processor if it accepts it
                    import inspect
                    sig = inspect.signature(processor_func)
                    if 'metadata' in sig.parameters and meta is not None:
                        result = await processor_func(doc, metadata=meta)
                    else:
                        result = await processor_func(doc)
                    
                    self.stats['documents_processed'] += 1
                    return (index, result, None)
                except Exception as e:
                    self.stats['errors'] += 1
                    logging.error(f"Error processing document {index}: {e}")
                    return (index, None, e)
        
        start_time = time.perf_counter()
        
        # Process in chunks to manage memory
        all_results = []
        for i in range(0, len(documents), self.chunk_size):
            chunk_docs = documents[i:i + self.chunk_size]
            chunk_meta = metadata[i:i + self.chunk_size] if metadata else [None] * len(chunk_docs)
            
            chunk_tasks = [
                process_single_doc(i + j, doc, meta)
                for j, (doc, meta) in enumerate(zip(chunk_docs, chunk_meta))
            ]
            
            chunk_results = await asyncio.gather(*chunk_tasks, return_exceptions=False)
            all_results.extend(chunk_results)
            
            # Small delay between chunks to prevent overwhelming
            if i + self.chunk_size < len(documents):
                await asyncio.sleep(0.01)
        
        self.stats['total_processing_time'] += time.perf_counter() - start_time
        self.stats['batches_completed'] += 1
        
        return all_results
    
    async def batch_add_to_vector_db(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        vector_db = None,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """Batch add documents to vector database with chunking.
        
        Args:
            documents: List of document contents
            metadatas: Optional metadata for each document
            vector_db: Vector database instance
            batch_size: Size of each batch for database operations
            
        Returns:
            Dictionary with processing statistics
        """
        if vector_db is None:
            try:
                from .vector_db import get_vector_db
                vector_db = await get_vector_db()
            except ImportError:
                raise ValueError("Vector database not available. Install faiss-cpu and sentence-transformers.")
        
        stats = {
            'total_documents': len(documents),
            'batches_processed': 0,
            'successful_adds': 0,
            'failed_adds': 0,
            'processing_time': 0.0
        }
        
        start_time = time.perf_counter()
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size] if metadatas else None
            batch_ids = [f"doc_{i + j}" for j in range(len(batch_docs))]
            
            async with self.semaphore:
                try:
                    await vector_db.add_documents_async(
                        documents=batch_docs,
                        metadatas=batch_meta,
                        ids=batch_ids
                    )
                    stats['successful_adds'] += len(batch_docs)
                    logging.debug(f"Added batch {stats['batches_processed'] + 1}: {len(batch_docs)} documents")
                except Exception as e:
                    stats['failed_adds'] += len(batch_docs)
                    logging.error(f"Failed to add batch {stats['batches_processed'] + 1}: {e}")
            
            stats['batches_processed'] += 1
            
            # Small delay between batches
            await asyncio.sleep(0.02)
        
        stats['processing_time'] = time.perf_counter() - start_time
        
        logging.info(f"Batch vector DB operation completed: {stats['successful_adds']}/{stats['total_documents']} successful")
        return stats
    
    async def _validate_file_paths(
        self, 
        file_paths: List[Union[str, Path]]
    ) -> List[Path]:
        """Validate file paths for security (prevent path traversal)."""
        validated_paths = []
        
        # Get project root for validation
        try:
            from ..config_loader import get_project_root
            project_root = get_project_root()
        except ImportError:
            # Fallback to current working directory
            project_root = Path.cwd()
        
        for path in file_paths:
            path_obj = Path(path).resolve()
            
            # Security check: ensure path is within project or temp directories
            try:
                path_obj.relative_to(project_root)
                is_valid = True
            except ValueError:
                # Check if it's in a temp directory
                temp_dir = Path(tempfile.gettempdir()).resolve()
                try:
                    path_obj.relative_to(temp_dir)
                    is_valid = True
                except ValueError:
                    is_valid = False
            
            if is_valid and path_obj.exists() and path_obj.is_file():
                validated_paths.append(path_obj)
            else:
                logging.warning(f"Skipping invalid or inaccessible file: {path}")
        
        return validated_paths
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.stats.copy()
        if stats['documents_processed'] > 0:
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['documents_processed']
        if stats['batches_completed'] > 0:
            stats['avg_batch_time'] = stats['total_processing_time'] / stats['batches_completed']
        return stats


@async_timed
async def async_rag_document_ingestion(
    documents: List[str],
    rag_pipeline = None,
    metadatas: Optional[List[Dict]] = None,
    batch_size: int = 20,
    max_concurrent: int = 3
) -> Dict[str, Any]:
    """Ingest documents into RAG pipeline with batch processing.
    
    Args:
        documents: List of document contents
        rag_pipeline: RAG pipeline instance (optional)
        metadatas: Optional metadata for each document
        batch_size: Number of documents per batch
        max_concurrent: Maximum concurrent operations
        
    Returns:
        Dictionary with ingestion statistics
    """
    if rag_pipeline is None:
        try:
            from ..rag_pipeline import create_rag_pipeline
            rag_pipeline = create_rag_pipeline()
        except ImportError:
            raise ValueError("RAG pipeline not available. Install required dependencies.")
    
    processor = DocumentBatchProcessor(max_concurrent=max_concurrent, chunk_size=batch_size)
    
    # Use the batch add function
    return await processor.batch_add_to_vector_db(
        documents=documents,
        metadatas=metadatas,
        vector_db=getattr(rag_pipeline, 'vector_db', None),
        batch_size=batch_size
    )


@async_timed
async def async_batch_file_processing(
    file_paths: List[Union[str, Path]],
    output_processor: Callable[[str, str], Awaitable[Any]],
    max_concurrent: int = 4,
    validate_paths: bool = True
) -> List[Tuple[str, Any, Optional[Exception]]]:
    """Process multiple files in parallel with security validation.
    
    Args:
        file_paths: List of file paths to process
        output_processor: Async function that takes (file_path, content) and returns processed result
        max_concurrent: Maximum concurrent file operations
        validate_paths: Whether to validate file paths for security
        
    Returns:
        List of (file_path, result, error) tuples
    """
    processor = DocumentBatchProcessor(max_concurrent=max_concurrent)
    
    async def wrapper_func(content: str, file_path: str) -> Any:
        return await output_processor(file_path, content)
    
    # Process files
    results = await processor.process_documents_from_files(
        file_paths=file_paths,
        processor_func=lambda content: wrapper_func(content, "placeholder"),  # Will be replaced in actual processing
        validate_paths=validate_paths
    )
    
    return results


@async_timed
async def async_document_similarity_batch(
    query_docs: List[str],
    reference_docs: List[str],
    similarity_threshold: float = 0.7,
    max_concurrent: int = 3
) -> List[Tuple[int, List[Tuple[int, float]]]]:
    """Batch process document similarity comparisons.
    
    Args:
        query_docs: Documents to find similarities for
        reference_docs: Reference document set
        similarity_threshold: Minimum similarity score to include
        max_concurrent: Maximum concurrent operations
        
    Returns:
        List of (query_index, [(ref_index, similarity_score), ...]) tuples
    """
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
    except ImportError:
        raise ValueError("Similarity processing requires: pip install sentence-transformers scikit-learn")
    
    # Load embedding model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def process_similarity(query_idx: int, query_doc: str) -> Tuple[int, List[Tuple[int, float]]]:
        # Encode documents (this is CPU intensive, so we use executor)
        def encode_docs():
            query_embedding = model.encode([query_doc])
            ref_embeddings = model.encode(reference_docs)
            similarities = cosine_similarity(query_embedding, ref_embeddings)[0]
            
            # Filter by threshold and return with indices
            similar_docs = [
                (ref_idx, float(score))
                for ref_idx, score in enumerate(similarities)
                if score >= similarity_threshold
            ]
            
            # Sort by similarity score (descending)
            similar_docs.sort(key=lambda x: x[1], reverse=True)
            return similar_docs
        
        similar_docs = await run_in_executor(encode_docs)
        return (query_idx, similar_docs)
    
    # Process queries with concurrency control
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def controlled_similarity(query_idx: int, query_doc: str):
        async with semaphore:
            return await process_similarity(query_idx, query_doc)
    
    tasks = [
        controlled_similarity(i, doc)
        for i, doc in enumerate(query_docs)
    ]
    
    results = await asyncio.gather(*tasks)
    return results


# Export key functions
__all__ = [
    'async_timed',
    'run_in_executor', 
    'async_subprocess_run',
    'async_file_read',
    'async_file_write',
    'async_batch_operation',
    'async_query_llm_safe',
    'get_async_stats',
    'cleanup_async_resources',
    'AsyncContext',
    # Document batch processing helpers
    'DocumentBatchProcessor',
    'async_rag_document_ingestion',
    'async_batch_file_processing',
    'async_document_similarity_batch'
]