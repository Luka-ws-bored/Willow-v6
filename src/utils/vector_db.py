"""
Vector Database Module for Willow v6.
Provides efficient storage and retrieval of document embeddings using FAISS.
"""

import os
import pickle
import logging
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
from threading import RLock
import weakref

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    VECTOR_DB_AVAILABLE = True
except ImportError as e:
    logging.error(f"Vector DB dependencies not available: {e}")
    VECTOR_DB_AVAILABLE = False
    # Dummy classes for type hints when dependencies unavailable
    class SentenceTransformer:
        pass
    faiss = None
    np = None

try:
    from .file_ops import get_file_ops
    from .async_helpers import run_in_executor
    from ..config_loader import get_config
except ImportError:
    # Fallback for standalone usage
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.file_ops import get_file_ops
    from utils.async_helpers import run_in_executor
    from config_loader import get_config


class VectorDBError(Exception):
    """Custom exception for vector database errors."""
    pass


class VectorDBMetrics:
    """Performance metrics for vector database operations."""
    
    def __init__(self):
        self.metrics = {
            'embeddings_created': 0,
            'documents_added': 0,
            'searches_performed': 0,
            'embedding_time': [],
            'search_time': [],
            'index_size': 0,
            'cache_hits': 0
        }
        self._lock = RLock()
    
    def record_embedding_time(self, time_seconds: float) -> None:
        """Record embedding creation time."""
        with self._lock:
            self.metrics['embedding_time'].append(time_seconds)
    
    def record_search_time(self, time_seconds: float) -> None:
        """Record search operation time."""
        with self._lock:
            self.metrics['search_time'].append(time_seconds)
    
    def increment_documents_added(self, count: int = 1) -> None:
        """Increment documents added counter."""
        with self._lock:
            self.metrics['documents_added'] += count
    
    def increment_searches(self) -> None:
        """Increment search counter."""
        with self._lock:
            self.metrics['searches_performed'] += 1
    
    def increment_cache_hits(self) -> None:
        """Increment cache hit counter."""
        with self._lock:
            self.metrics['cache_hits'] += 1
    
    def update_index_size(self, size: int) -> None:
        """Update index size."""
        with self._lock:
            self.metrics['index_size'] = size
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        with self._lock:
            summary = self.metrics.copy()
            
            if self.metrics['embedding_time']:
                summary['avg_embedding_time'] = sum(self.metrics['embedding_time']) / len(self.metrics['embedding_time'])
                summary['max_embedding_time'] = max(self.metrics['embedding_time'])
            
            if self.metrics['search_time']:
                summary['avg_search_time'] = sum(self.metrics['search_time']) / len(self.metrics['search_time'])
                summary['max_search_time'] = max(self.metrics['search_time'])
            
            if self.metrics['searches_performed'] > 0:
                summary['cache_hit_rate'] = self.metrics['cache_hits'] / self.metrics['searches_performed']
            
            return summary


class VectorDB:
    """High-performance vector database using FAISS with async support."""
    
    def __init__(
        self,
        embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
        db_path: Optional[Union[str, Path]] = None,
        dimension: Optional[int] = None,
        index_type: str = 'flat',
        cache_embeddings: bool = True
    ):
        """Initialize vector database.
        
        Args:
            embedding_model: Name of the sentence transformer model
            db_path: Path to store database files
            dimension: Embedding dimension (auto-detected if None)
            index_type: FAISS index type ('flat', 'ivf', 'hnsw')
            cache_embeddings: Whether to cache embeddings
        """
        if not VECTOR_DB_AVAILABLE:
            raise VectorDBError("Vector DB dependencies not available. Install: pip install faiss-cpu sentence-transformers")
        
        try:
            self.config = get_config()
            self.file_ops = get_file_ops()
        except Exception:
            # Fallback for testing without full config
            self.config = None
            self.file_ops = None
        
        # Configuration
        self.embedding_model_name = embedding_model
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.cwd() / 'data' / 'vector_db' if not self.config else self.config.project_root / 'data' / 'vector_db'
        self.index_type = index_type
        self.cache_embeddings = cache_embeddings
        
        # File paths
        self.index_file = self.db_path / 'index.faiss'
        self.metadata_file = self.db_path / 'metadata.pkl'
        self.config_file = self.db_path / 'config.pkl'
        
        # State
        self.model: Optional[SentenceTransformer] = None
        self.index: Optional[Any] = None
        self.metadata: List[Dict[str, Any]] = []
        self.dimension = dimension
        self._embedding_cache = weakref.WeakValueDictionary() if cache_embeddings else {}
        self._index_lock = RLock()
        
        # Metrics
        self.metrics = VectorDBMetrics()
        
        # Initialize
        self._ensure_directory()
        self._load_or_create()
        
        logging.info(f"VectorDB initialized with model: {embedding_model}, path: {self.db_path}")
    
    def _ensure_directory(self) -> None:
        """Ensure database directory exists with proper permissions."""
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            # Validate path is within project bounds
            self.file_ops.validate_path(self.db_path)
        except Exception as e:
            raise VectorDBError(f"Failed to create database directory: {e}")
    
    def _get_model(self) -> SentenceTransformer:
        """Get or create the embedding model."""
        if self.model is None:
            try:
                # Use cache directory for model files
                cache_dir = self.config.project_root / '.cache' / 'embeddings'
                cache_dir.mkdir(parents=True, exist_ok=True)
                
                self.model = SentenceTransformer(
                    self.embedding_model_name,
                    cache_folder=str(cache_dir)
                )
                
                # Auto-detect dimension if not provided
                if self.dimension is None:
                    self.dimension = self.model.get_sentence_embedding_dimension()
                    
                logging.info(f"Embedding model loaded: {self.embedding_model_name}, dimension: {self.dimension}")
                
            except Exception as e:
                raise VectorDBError(f"Failed to load embedding model: {e}")
        
        return self.model
    
    def _create_index(self) -> Any:
        """Create a new FAISS index based on configuration."""
        if self.dimension is None:
            # Need to load model to get dimension
            self._get_model()
        
        if self.index_type == 'flat':
            index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == 'ivf':
            # IVF index for larger datasets
            quantizer = faiss.IndexFlatL2(self.dimension)
            index = faiss.IndexIVFFlat(quantizer, self.dimension, min(100, max(1, self.dimension // 4)))
        elif self.index_type == 'hnsw':
            # HNSW index for fast approximate search
            index = faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise VectorDBError(f"Unsupported index type: {self.index_type}")
        
        return index
    
    def _load_or_create(self) -> None:
        """Load existing index or create new one."""
        try:
            if self.index_file.exists() and self.metadata_file.exists():
                self._load_index()
            else:
                self.index = self._create_index()
                self.metadata = []
                logging.info("Created new vector database index")
        except Exception as e:
            logging.error(f"Failed to load/create index: {e}")
            # Fallback to new index
            self.index = self._create_index()
            self.metadata = []
    
    def _load_index(self) -> None:
        """Load existing index and metadata."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata
            with open(self.metadata_file, 'rb') as f:
                self.metadata = pickle.load(f)
            
            # Load configuration if exists
            if self.config_file.exists():
                with open(self.config_file, 'rb') as f:
                    config = pickle.load(f)
                    self.dimension = config.get('dimension', self.dimension)
                    self.embedding_model_name = config.get('embedding_model', self.embedding_model_name)
            
            # Update metrics
            self.metrics.update_index_size(self.index.ntotal if self.index else 0)
            
            logging.info(f"Loaded vector database: {len(self.metadata)} documents, index size: {self.index.ntotal if self.index else 0}")
            
        except Exception as e:
            raise VectorDBError(f"Failed to load index: {e}")
    
    def _save_index(self) -> None:
        """Save index and metadata to disk."""
        try:
            with self._index_lock:
                # Save FAISS index
                faiss.write_index(self.index, str(self.index_file))
                
                # Save metadata
                with open(self.metadata_file, 'wb') as f:
                    pickle.dump(self.metadata, f)
                
                # Save configuration
                config = {
                    'dimension': self.dimension,
                    'embedding_model': self.embedding_model_name,
                    'index_type': self.index_type
                }
                with open(self.config_file, 'wb') as f:
                    pickle.dump(config, f)
                
                # Update metrics
                self.metrics.update_index_size(self.index.ntotal if self.index else 0)
                
            logging.debug(f"Vector database saved: {len(self.metadata)} documents")
            
        except Exception as e:
            raise VectorDBError(f"Failed to save index: {e}")
    
    def _get_embeddings(self, texts: List[str]):
        """Get embeddings for texts with caching."""
        if not VECTOR_DB_AVAILABLE:
            raise VectorDBError("Vector DB dependencies not available")
        
        model = self._get_model()
        
        if not self.cache_embeddings:
            return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        
        # Check cache for existing embeddings
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = hash(text)
            if cache_key in self._embedding_cache:
                cached_embeddings.append((i, self._embedding_cache[cache_key]))
                self.metrics.increment_cache_hits()
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = model.encode(uncached_texts, convert_to_numpy=True, show_progress_bar=False)
            
            # Cache new embeddings
            for text, embedding in zip(uncached_texts, new_embeddings):
                cache_key = hash(text)
                self._embedding_cache[cache_key] = embedding
        else:
            new_embeddings = np.array([])
        
        # Combine cached and new embeddings in correct order
        all_embeddings = np.zeros((len(texts), self.dimension), dtype=np.float32)
        
        # Insert cached embeddings
        for i, embedding in cached_embeddings:
            all_embeddings[i] = embedding
        
        # Insert new embeddings
        for i, embedding in zip(uncached_indices, new_embeddings):
            all_embeddings[i] = embedding
        
        return all_embeddings
    
    async def add_documents_async(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the vector database asynchronously."""
        if not documents:
            return
        
        if metadatas and len(metadatas) != len(documents):
            raise VectorDBError("Number of metadatas must match number of documents")
        
        if ids and len(ids) != len(documents):
            raise VectorDBError("Number of ids must match number of documents")
        
        start_time = time.perf_counter()
        
        try:
            # Generate embeddings asynchronously
            embeddings = await run_in_executor(self._get_embeddings, documents)
            
            # Add to index
            with self._index_lock:
                if self.index is None:
                    self.index = self._create_index()
                
                # Train index if needed (for IVF)
                if self.index_type == 'ivf' and not self.index.is_trained:
                    if len(embeddings) >= self.index.nlist:
                        self.index.train(embeddings)
                    else:
                        logging.warning(f"Not enough data to train IVF index (need {self.index.nlist}, got {len(embeddings)})")
                
                # Add embeddings to index
                self.index.add(embeddings)
                
                # Add metadata
                for i, doc in enumerate(documents):
                    doc_metadata = {
                        'text': doc,
                        'id': ids[i] if ids else f"doc_{len(self.metadata)}",
                        'index': len(self.metadata)
                    }
                    
                    if metadatas:
                        doc_metadata.update(metadatas[i])
                    
                    self.metadata.append(doc_metadata)
                
                # Save to disk
                await run_in_executor(self._save_index)
            
            # Update metrics
            embedding_time = time.perf_counter() - start_time
            self.metrics.record_embedding_time(embedding_time)
            self.metrics.increment_documents_added(len(documents))
            
            logging.info(f"Added {len(documents)} documents to vector database in {embedding_time:.3f}s")
            
        except Exception as e:
            raise VectorDBError(f"Failed to add documents: {e}")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to the vector database (synchronous)."""
        asyncio.run(self.add_documents_async(documents, metadatas, ids))
    
    async def search_async(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar documents asynchronously."""
        if not query.strip():
            return []
        
        start_time = time.perf_counter()
        
        try:
            # Generate query embedding
            query_embedding = await run_in_executor(self._get_embeddings, [query])
            
            with self._index_lock:
                if self.index is None or self.index.ntotal == 0:
                    return []
                
                # Perform search
                distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
            
            # Prepare results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                if idx < len(self.metadata):
                    metadata = self.metadata[idx].copy()
                    
                    # Apply metadata filter if provided
                    if filter_metadata:
                        if not all(metadata.get(k) == v for k, v in filter_metadata.items()):
                            continue
                    
                    # Convert distance to similarity score (higher is better)
                    similarity_score = 1.0 / (1.0 + distance)
                    results.append((metadata, similarity_score))
            
            # Update metrics
            search_time = time.perf_counter() - start_time
            self.metrics.record_search_time(search_time)
            self.metrics.increment_searches()
            
            logging.debug(f"Vector search completed in {search_time:.3f}s, found {len(results)} results")
            
            return results
            
        except Exception as e:
            raise VectorDBError(f"Search failed: {e}")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for similar documents (synchronous)."""
        return asyncio.run(self.search_async(query, top_k, filter_metadata))
    
    async def get_document_by_id_async(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID asynchronously."""
        with self._index_lock:
            for metadata in self.metadata:
                if metadata.get('id') == doc_id:
                    return metadata.copy()
        return None
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID (synchronous)."""
        return asyncio.run(self.get_document_by_id_async(doc_id))
    
    def clear_cache(self) -> None:
        """Clear embedding cache."""
        if self.cache_embeddings:
            self._embedding_cache.clear()
        logging.info("Vector DB cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._index_lock:
            return {
                'total_documents': len(self.metadata),
                'index_size': self.index.ntotal if self.index else 0,
                'dimension': self.dimension,
                'embedding_model': self.embedding_model_name,
                'index_type': self.index_type,
                'db_path': str(self.db_path),
                'cache_enabled': self.cache_embeddings,
                'metrics': self.metrics.get_summary()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check of vector database."""
        try:
            status = {
                'db_available': VECTOR_DB_AVAILABLE,
                'index_loaded': self.index is not None,
                'model_loaded': self.model is not None,
                'db_path_exists': self.db_path.exists(),
                'total_documents': len(self.metadata),
                'index_size': self.index.ntotal if self.index else 0,
                'dimension': self.dimension
            }
            
            # Test search if data exists
            if self.index and self.index.ntotal > 0:
                try:
                    test_results = self.search("test query", top_k=1)
                    status['search_working'] = True
                    status['test_search_results'] = len(test_results)
                except Exception as e:
                    status['search_working'] = False
                    status['search_error'] = str(e)
            else:
                status['search_working'] = None  # No data to test
            
            return status
            
        except Exception as e:
            return {
                'db_available': False,
                'error': str(e),
                'health_check_failed': True
            }


# Global vector database instance (initialized lazily)
_vector_db: Optional[VectorDB] = None


async def get_vector_db(
    embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
    db_path: Optional[Union[str, Path]] = None
) -> VectorDB:
    """Get or create the global vector database instance."""
    global _vector_db
    
    if _vector_db is None:
        if db_path is None:
            config = get_config()
            db_path = config.project_root / 'data' / 'vector_db'
        
        _vector_db = VectorDB(
            embedding_model=embedding_model,
            db_path=db_path
        )
    
    return _vector_db


# Legacy compatibility functions (implement the original interface)
def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embeddings for list of texts."""
    if not VECTOR_DB_AVAILABLE:
        raise NotImplementedError("Vector DB dependencies not available")
    
    db = VectorDB()
    embeddings = db._get_embeddings(texts)
    return embeddings.tolist()


def create_index(embeddings: List[List[float]], ids: List[str], index_path: str) -> None:
    """Create and persist a vector index (FAISS)."""
    if not VECTOR_DB_AVAILABLE:
        raise NotImplementedError("Vector DB dependencies not available")
    
    db = VectorDB(db_path=Path(index_path).parent)
    # Convert to text documents for storage (this is a simplified approach)
    documents = [f"Document {i}" for i in ids]
    metadatas = [{'id': doc_id} for doc_id in ids]
    db.add_documents(documents, metadatas, ids)


def load_index(index_path: str) -> VectorDB:
    """Load and return an index object."""
    if not VECTOR_DB_AVAILABLE:
        raise NotImplementedError("Vector DB dependencies not available")
    
    return VectorDB(db_path=Path(index_path).parent)


def search_index(
    query_embedding: List[float], 
    top_k: int = 5,
    db_path: str = None
) -> List[Dict[str, Any]]:
    """Search index and return top_k results."""
    if not VECTOR_DB_AVAILABLE:
        raise NotImplementedError("Vector DB dependencies not available")
    
    # This is a simplified approach - in practice, you'd want to use the full VectorDB interface
    db = VectorDB(db_path=db_path)
    # Convert embedding back to query (this is imperfect but maintains compatibility)
    dummy_query = "search query"
    results = db.search(dummy_query, top_k)
    
    return [
        {
            'id': metadata.get('id', ''),
            'score': score,
            'metadata': metadata
        }
        for metadata, score in results
    ]


# Export key classes and functions
__all__ = [
    'VectorDB',
    'VectorDBError',
    'VectorDBMetrics',
    'get_vector_db',
    'embed_texts',
    'create_index', 
    'load_index',
    'search_index',
    'VECTOR_DB_AVAILABLE'
]