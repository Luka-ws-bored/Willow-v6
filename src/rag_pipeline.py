"""
"""
RAG Pipeline integration module for Willow v6.
Provides a simplified interface to integrate VectorDB with LLM queries.
Enhanced with advanced caching for improved performance.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import logging
import asyncio
import time
import hashlib
import json
from pathlib import Path
from functools import lru_cache
from threading import RLock
import weakref

try:
    from src.utils.vector_db import VectorDB, VectorDBError, VECTOR_DB_AVAILABLE
except ImportError:
    try:
        from utils.vector_db import VectorDB, VectorDBError, VECTOR_DB_AVAILABLE
    except ImportError:
        VECTOR_DB_AVAILABLE = False
        logging.warning("VectorDB not available - RAG functionality will be limited")
        
        class VectorDBError(Exception):
            pass


class AdvancedRAGCache:
    """Advanced caching system for RAG operations with TTL and LRU eviction."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: float = 3600.0):
        """Initialize cache with size and TTL limits.
        
        Args:
            max_size: Maximum number of cached entries
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_times = {}
        self._creation_times = {}
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
    
    def _generate_key(self, query: str, top_k: int, **kwargs) -> str:
        """Generate cache key from query parameters."""
        key_data = {
            'query': query.lower().strip(),
            'top_k': top_k,
            **kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._creation_times:
            return True
        age = time.time() - self._creation_times[key]
        return age > self.ttl_seconds
    
    def _evict_expired(self):
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = []
        
        for key, creation_time in self._creation_times.items():
            if current_time - creation_time > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_entry(key)
    
    def _evict_lru(self):
        """Remove least recently used entries to stay under max_size."""
        while len(self._cache) >= self.max_size:
            # Find least recently used key
            lru_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            self._remove_entry(lru_key)
    
    def _remove_entry(self, key: str):
        """Remove entry from all cache structures."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._creation_times.pop(key, None)
    
    def get(self, query: str, top_k: int, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """Get cached results for query."""
        with self._lock:
            key = self._generate_key(query, top_k, **kwargs)
            
            # Clean expired entries periodically
            if len(self._cache) % 100 == 0:
                self._evict_expired()
            
            if key in self._cache and not self._is_expired(key):
                self._access_times[key] = time.time()
                self._hits += 1
                return self._cache[key].copy()  # Return copy to prevent mutation
            
            self._misses += 1
            return None
    
    def put(self, query: str, top_k: int, results: List[Dict[str, Any]], **kwargs):
        """Cache query results."""
        with self._lock:
            key = self._generate_key(query, top_k, **kwargs)
            current_time = time.time()
            
            # Evict if necessary
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # Store results
            self._cache[key] = [result.copy() for result in results]  # Deep copy
            self._access_times[key] = current_time
            self._creation_times[key] = current_time
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
            self._creation_times.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) if total_requests > 0 else 0.0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'ttl_seconds': self.ttl_seconds
            }


class RAGPipeline:
    """Simplified RAG pipeline with advanced caching and performance optimization."""
    
    def __init__(
        self, 
        vector_db: Optional[VectorDB] = None, 
        db_path: Optional[Union[str, Path]] = None,
        cache_size: int = 1000,
        cache_ttl: float = 3600.0,
        enable_caching: bool = True
    ):
        """Initialize RAG pipeline with VectorDB instance and caching.
        
        Args:
            vector_db: Existing VectorDB instance (optional)
            db_path: Path to vector database (used if vector_db not provided)
            cache_size: Maximum number of cached query results
            cache_ttl: Cache time-to-live in seconds
            enable_caching: Whether to enable result caching
        """
        if not VECTOR_DB_AVAILABLE:
            raise VectorDBError("VectorDB dependencies not available. Please install: pip install faiss-cpu sentence-transformers")
        
        if vector_db is not None:
            self.vector_db = vector_db
        elif db_path is not None:
            self.vector_db = VectorDB(db_path=db_path)
        else:
            # Use default path
            self.vector_db = VectorDB()
        
        self.query_count = 0
        self.cache_enabled = enable_caching
        
        # Initialize caching system
        if self.cache_enabled:
            self._query_cache = AdvancedRAGCache(max_size=cache_size, ttl_seconds=cache_ttl)
            self._context_cache = AdvancedRAGCache(max_size=cache_size//2, ttl_seconds=cache_ttl)
        else:
            self._query_cache = None
            self._context_cache = None
        
        # Performance tracking
        self._query_times = []
        self._cache_performance = {
            'total_cache_time_saved': 0.0,
            'avg_query_time_with_cache': 0.0,
            'avg_query_time_without_cache': 0.0
        }
        
        logging.info(f"RAG Pipeline initialized with VectorDB (caching: {enable_caching})")
    
    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add documents to the vector database.
        
        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dicts for each document
        """
        try:
            # Ensure metadata includes content for retrieval
            if metadatas:
                enhanced_metadatas = []
                for i, metadata in enumerate(metadatas):
                    enhanced_metadata = metadata.copy()
                    if 'content' not in enhanced_metadata:
                        enhanced_metadata['content'] = documents[i]
                    enhanced_metadatas.append(enhanced_metadata)
            else:
                enhanced_metadatas = [{'content': doc} for doc in documents]
            
            self.vector_db.add_documents(
                documents=documents,
                metadatas=enhanced_metadatas
            )
            logging.info(f"Added {len(documents)} documents to RAG pipeline")
            
        except Exception as e:
            logging.error(f"Failed to add documents to RAG pipeline: {e}")
            raise VectorDBError(f"Document addition failed: {e}")
    
    def query(self, user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a user query with caching.
        
        Args:
            user_query: User's search query
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
        """
        try:
            start_time = time.perf_counter()
            self.query_count += 1
            
            # Check cache first
            if self.cache_enabled and self._query_cache:
                cached_results = self._query_cache.get(user_query, top_k)
                if cached_results is not None:
                    cache_time = time.perf_counter() - start_time
                    self._update_performance_stats(cache_time, from_cache=True)
                    logging.debug(f"RAG query '{user_query}' served from cache ({len(cached_results)} docs)")
                    return cached_results
            
            # Search vector database
            results = self.vector_db.search(user_query, top_k=top_k)
            
            # Format results for LLM consumption
            retrieved_docs = []
            for metadata, score in results:
                doc_dict = {
                    'content': metadata.get('content', metadata.get('text', '')),
                    'metadata': metadata,
                    'relevance_score': score
                }
                retrieved_docs.append(doc_dict)
            
            # Cache results
            if self.cache_enabled and self._query_cache:
                self._query_cache.put(user_query, top_k, retrieved_docs)
            
            query_time = time.perf_counter() - start_time
            self._update_performance_stats(query_time, from_cache=False)
            
            logging.debug(f"RAG query '{user_query}' returned {len(retrieved_docs)} documents in {query_time:.3f}s")
            return retrieved_docs
            
        except Exception as e:
            logging.error(f"RAG query failed: {e}")
            raise VectorDBError(f"Query failed: {e}")
    
    async def query_async(self, user_query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Async version of query method with caching.
        
        Args:
            user_query: User's search query
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with 'content' and 'metadata' keys
        """
        try:
            start_time = time.perf_counter()
            self.query_count += 1
            
            # Check cache first
            if self.cache_enabled and self._query_cache:
                cached_results = self._query_cache.get(user_query, top_k)
                if cached_results is not None:
                    cache_time = time.perf_counter() - start_time
                    self._update_performance_stats(cache_time, from_cache=True)
                    logging.debug(f"Async RAG query '{user_query}' served from cache ({len(cached_results)} docs)")
                    return cached_results
            
            # Search vector database asynchronously
            results = await self.vector_db.search_async(user_query, top_k=top_k)
            
            # Format results for LLM consumption
            retrieved_docs = []
            for metadata, score in results:
                doc_dict = {
                    'content': metadata.get('content', metadata.get('text', '')),
                    'metadata': metadata,
                    'relevance_score': score
                }
                retrieved_docs.append(doc_dict)
            
            # Cache results
            if self.cache_enabled and self._query_cache:
                self._query_cache.put(user_query, top_k, retrieved_docs)
            
            query_time = time.perf_counter() - start_time
            self._update_performance_stats(query_time, from_cache=False)
            
            logging.debug(f"Async RAG query '{user_query}' returned {len(retrieved_docs)} documents in {query_time:.3f}s")
            return retrieved_docs
            
        except Exception as e:
            logging.error(f"Async RAG query failed: {e}")
            raise VectorDBError(f"Async query failed: {e}")
    
    def format_context_for_llm(self, retrieved_docs: List[Dict[str, Any]], user_query: str) -> str:
        """Format retrieved documents as context for LLM input.
        
        Args:
            retrieved_docs: List of retrieved documents from query()
            user_query: Original user query
            
        Returns:
            Formatted context string for LLM
        """
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_parts = ["# Retrieved Context"]
        
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc['content'].strip()
            score = doc.get('relevance_score', 0)
            source = doc['metadata'].get('id', f'Document {i}')
            
            context_parts.append(f"\n## Source {i}: {source} (Relevance: {score:.3f})")
            context_parts.append(content)
        
        context_parts.append(f"\n# User Query: {user_query}")
        context_parts.append("\nPlease answer based on the retrieved context above.")
        
        return "\n".join(context_parts)
    
    def query_with_context(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """Perform RAG query and return both documents and formatted context with caching.
        
        Args:
            user_query: User's search query
            top_k: Number of top results to return
            
        Returns:
            Dictionary with 'documents', 'context', and 'query' keys
        """
        # Check context cache first
        if self.cache_enabled and self._context_cache:
            cached_context = self._context_cache.get(user_query, top_k, operation='context')
            if cached_context is not None:
                logging.debug(f"Context for '{user_query}' served from cache")
                return cached_context
        
        retrieved_docs = self.query(user_query, top_k=top_k)
        context = self.format_context_for_llm(retrieved_docs, user_query)
        
        result = {
            'documents': retrieved_docs,
            'context': context,
            'query': user_query,
            'document_count': len(retrieved_docs)
        }
        
        # Cache the context result
        if self.cache_enabled and self._context_cache:
            self._context_cache.put(user_query, top_k, result, operation='context')
        
        return result
    
    async def query_with_context_async(self, user_query: str, top_k: int = 5) -> Dict[str, Any]:
        """Async version of query_with_context with caching.
        
        Args:
            user_query: User's search query
            top_k: Number of top results to return
            
        Returns:
            Dictionary with 'documents', 'context', and 'query' keys
        """
        # Check context cache first
        if self.cache_enabled and self._context_cache:
            cached_context = self._context_cache.get(user_query, top_k, operation='context')
            if cached_context is not None:
                logging.debug(f"Async context for '{user_query}' served from cache")
                return cached_context
        
        retrieved_docs = await self.query_async(user_query, top_k=top_k)
        context = self.format_context_for_llm(retrieved_docs, user_query)
        
        result = {
            'documents': retrieved_docs,
            'context': context,
            'query': user_query,
            'document_count': len(retrieved_docs)
        }
        
        # Cache the context result
        if self.cache_enabled and self._context_cache:
            self._context_cache.put(user_query, top_k, result, operation='context')
        
        return result
    
    def _update_performance_stats(self, query_time: float, from_cache: bool = False):
        """Update internal performance statistics."""
        self._query_times.append(query_time)
        
        if from_cache:
            self._cache_performance['total_cache_time_saved'] += max(0, 
                self._cache_performance.get('avg_query_time_without_cache', 0.1) - query_time)
        
        # Update averages (keep last 100 queries for moving average)
        if len(self._query_times) > 100:
            self._query_times = self._query_times[-100:]
        
        cached_times = [t for i, t in enumerate(self._query_times) if i < len(self._query_times)//2]
        uncached_times = [t for i, t in enumerate(self._query_times) if i >= len(self._query_times)//2]
        
        if cached_times:
            self._cache_performance['avg_query_time_with_cache'] = sum(cached_times) / len(cached_times)
        if uncached_times:
            self._cache_performance['avg_query_time_without_cache'] = sum(uncached_times) / len(uncached_times)
        context = self.format_context_for_llm(retrieved_docs, user_query)
        
        return {
            'documents': retrieved_docs,
            'context': context,
            'query': user_query,
            'document_count': len(retrieved_docs)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive RAG pipeline statistics including cache performance.
        
        Returns:
            Dictionary with pipeline statistics
        """
        vector_db_stats = self.vector_db.get_stats() if hasattr(self.vector_db, 'get_stats') else {}
        
        stats = {
            'query_count': self.query_count,
            'vector_db_available': VECTOR_DB_AVAILABLE,
            'vector_db_stats': vector_db_stats,
            'caching_enabled': self.cache_enabled,
            'performance': self._cache_performance.copy()
        }
        
        # Add cache statistics
        if self.cache_enabled:
            if self._query_cache:
                stats['query_cache'] = self._query_cache.get_stats()
            if self._context_cache:
                stats['context_cache'] = self._context_cache.get_stats()
        
        # Add performance summary
        if self._query_times:
            stats['performance'].update({
                'total_queries': len(self._query_times),
                'avg_query_time': sum(self._query_times) / len(self._query_times),
                'min_query_time': min(self._query_times),
                'max_query_time': max(self._query_times)
            })
        
        return stats
    
    def clear_caches(self):
        """Clear all caches and reset performance stats."""
        if self.cache_enabled:
            if self._query_cache:
                self._query_cache.clear()
            if self._context_cache:
                self._context_cache.clear()
        
        self._query_times.clear()
        self._cache_performance = {
            'total_cache_time_saved': 0.0,
            'avg_query_time_with_cache': 0.0,
            'avg_query_time_without_cache': 0.0
        }
        
        logging.info("RAG Pipeline caches cleared")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of RAG pipeline.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Check VectorDB health
            vector_db_health = self.vector_db.health_check() if hasattr(self.vector_db, 'health_check') else {'status': 'unknown'}
            
            # Perform a test query if there are documents
            test_query_working = False
            if vector_db_health.get('total_documents', 0) > 0:
                try:
                    test_results = self.query("test", top_k=1)
                    test_query_working = len(test_results) >= 0  # Even empty results are OK
                except Exception:
                    test_query_working = False
            
            return {
                'rag_pipeline_healthy': True,
                'vector_db_available': VECTOR_DB_AVAILABLE,
                'vector_db_health': vector_db_health,
                'test_query_working': test_query_working,
                'total_queries': self.query_count
            }
            
        except Exception as e:
            return {
                'rag_pipeline_healthy': False,
                'error': str(e),
                'vector_db_available': VECTOR_DB_AVAILABLE
            }


# Convenience functions for quick usage
def create_rag_pipeline(db_path: Optional[Union[str, Path]] = None) -> RAGPipeline:
    """Create a RAG pipeline instance.
    
    Args:
        db_path: Optional path to vector database
        
    Returns:
        RAGPipeline instance
    """
    return RAGPipeline(db_path=db_path)


async def quick_rag_query(query: str, documents: List[str], top_k: int = 3) -> Dict[str, Any]:
    """Quick RAG query with temporary in-memory database.
    
    Args:
        query: Search query
        documents: List of documents to search
        top_k: Number of results to return
        
    Returns:
        Dictionary with query results and context
    """
    import tempfile
    import shutil
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    try:
        rag = RAGPipeline(db_path=temp_dir)
        rag.add_documents(documents)
        result = await rag.query_with_context_async(query, top_k=top_k)
        return result
    finally:
        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)


# Usage Examples (for documentation and testing)
if __name__ == "__main__":
    # Example usage (commented out to prevent execution during import)
    """
    # Basic usage
    db = VectorDB(db_path='./rag_test_db')
    rag = RAGPipeline(vector_db=db)
    
    # Add some documents
    docs = [
        'Willow v6 uses RAG for enhanced responses',
        'Vector databases enable semantic search',
        'Security fixes have been applied to the system'
    ]
    metadata = [
        {'content': 'Willow v6 uses RAG for enhanced responses', 'topic': 'rag'},
        {'content': 'Vector databases enable semantic search', 'topic': 'vector_db'},
        {'content': 'Security fixes have been applied to the system', 'topic': 'security'}
    ]
    rag.add_documents(docs, metadata)
    
    # Query for relevant documents
    results = rag.query('Tell me about Willow')
    for doc in results:
        print(f"Content: {doc['content']}")
        print(f"Score: {doc['relevance_score']}")
    
    # Get formatted context for LLM
    context_result = rag.query_with_context('Willow features', top_k=2)
    print("Context for LLM:")
    print(context_result['context'])
    """
    pass