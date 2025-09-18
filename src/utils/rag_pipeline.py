"""
RAG Pipeline Module for Willow v6.
Provides retrieval-augmented generation using LangChain with security and performance optimizations.
"""

import asyncio
import logging
import time
import weakref
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Generator, Tuple
from functools import lru_cache
from threading import RLock
from contextlib import asynccontextmanager

try:
    # LangChain imports
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader, DirectoryLoader
    from langchain_community.vectorstores import FAISS
    from langchain.docstore.document import Document
    from langchain.schema.retriever import BaseRetriever
    from langchain.schema.vectorstore import VectorStore
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    # RAGAS imports for evaluation
    try:
        from datasets import Dataset
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from ragas import evaluate
        RAGAS_AVAILABLE = True
    except ImportError:
        RAGAS_AVAILABLE = False
        logging.warning("RAGAS not available - evaluation features will be limited")
        
except ImportError as e:
    logging.error(f"Required LangChain dependencies not available: {e}")
    raise ImportError(
        "Please install required dependencies: "
        "pip install langchain langchain-community faiss-cpu sentence-transformers datasets ragas"
    )

try:
    from ..config_loader import get_config
    from .file_ops import get_file_ops
    from .async_helpers import run_in_executor, async_timed
    from .vector_db import get_vector_db, VectorDB, VECTOR_DB_AVAILABLE
except ImportError:
    # Fallback for standalone usage
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from config_loader import get_config
    from utils.file_ops import get_file_ops
    from utils.async_helpers import run_in_executor, async_timed
    try:
        from utils.vector_db import get_vector_db, VectorDB, VECTOR_DB_AVAILABLE
    except ImportError:
        VECTOR_DB_AVAILABLE = False
        logging.warning("VectorDB not available - using FAISS directly")


class RAGError(Exception):
    """Custom exception for RAG pipeline errors."""
    pass


class RAGMetrics:
    """Performance and quality metrics for RAG operations."""
    
    def __init__(self):
        self.metrics = {
            'retrieval_time': [],
            'generation_time': [],
            'total_queries': 0,
            'cache_hits': 0,
            'evaluation_scores': {},
            'document_count': 0,
            'vector_store_size': 0
        }
        self._lock = RLock()
    
    def record_retrieval_time(self, time_seconds: float) -> None:
        """Record retrieval operation timing."""
        with self._lock:
            self.metrics['retrieval_time'].append(time_seconds)
    
    def record_generation_time(self, time_seconds: float) -> None:
        """Record generation operation timing."""
        with self._lock:
            self.metrics['generation_time'].append(time_seconds)
    
    def increment_queries(self) -> None:
        """Increment total query count."""
        with self._lock:
            self.metrics['total_queries'] += 1
    
    def increment_cache_hits(self) -> None:
        """Increment cache hit count."""
        with self._lock:
            self.metrics['cache_hits'] += 1
    
    def record_evaluation_scores(self, scores: Dict[str, float]) -> None:
        """Record RAGAS evaluation scores."""
        with self._lock:
            for metric, score in scores.items():
                if metric not in self.metrics['evaluation_scores']:
                    self.metrics['evaluation_scores'][metric] = []
                self.metrics['evaluation_scores'][metric].append(score)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        with self._lock:
            summary = self.metrics.copy()
            
            if self.metrics['retrieval_time']:
                summary['avg_retrieval_time'] = sum(self.metrics['retrieval_time']) / len(self.metrics['retrieval_time'])
                summary['max_retrieval_time'] = max(self.metrics['retrieval_time'])
            
            if self.metrics['generation_time']:
                summary['avg_generation_time'] = sum(self.metrics['generation_time']) / len(self.metrics['generation_time'])
                
            if self.metrics['total_queries'] > 0:
                summary['cache_hit_rate'] = self.metrics['cache_hits'] / self.metrics['total_queries']
            
            # Average evaluation scores
            for metric, scores in self.metrics['evaluation_scores'].items():
                if scores:
                    summary[f'avg_{metric}'] = sum(scores) / len(scores)
            
            return summary


class SecureDocumentLoader:
    """Secure document loader with path validation and performance optimization."""
    
    def __init__(self, project_root: Path):
        self.file_ops = get_file_ops()
        self.project_root = project_root
        self._loader_cache = weakref.WeakValueDictionary()
    
    @lru_cache(maxsize=64)
    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        """Load a single document with caching and security validation."""
        validated_path = self.file_ops.validate_path(file_path)
        
        if not validated_path.exists():
            raise RAGError(f"Document not found: {validated_path}")
        
        if not validated_path.is_file():
            raise RAGError(f"Path is not a file: {validated_path}")
        
        try:
            loader = TextLoader(str(validated_path), encoding='utf-8')
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'file_path': str(validated_path),
                    'file_size': validated_path.stat().st_size,
                    'last_modified': validated_path.stat().st_mtime
                })
            
            return documents
            
        except Exception as e:
            raise RAGError(f"Failed to load document {validated_path}: {e}")
    
    def load_directory(self, dir_path: Union[str, Path], glob_pattern: str = "**/*.txt") -> List[Document]:
        """Load all documents from a directory with security validation."""
        validated_dir = self.file_ops.validate_path(dir_path)
        
        if not validated_dir.exists():
            raise RAGError(f"Directory not found: {validated_dir}")
        
        if not validated_dir.is_dir():
            raise RAGError(f"Path is not a directory: {validated_dir}")
        
        try:
            # Use secure file listing
            file_paths = list(self.file_ops.list_safe_files(validated_dir, glob_pattern, recursive=True))
            
            all_documents = []
            for file_path in file_paths:
                try:
                    documents = self.load_document(file_path)
                    all_documents.extend(documents)
                except RAGError as e:
                    logging.warning(f"Skipping file {file_path}: {e}")
                    continue
            
            logging.info(f"Loaded {len(all_documents)} documents from {validated_dir}")
            return all_documents
            
        except Exception as e:
            raise RAGError(f"Failed to load directory {validated_dir}: {e}")


class RAGPipeline:
    """Main RAG pipeline with async support and performance optimization."""
    
    def __init__(
        self,
        docs_path: Union[str, Path],
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        retrieval_k: int = 5,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_vector_db: bool = True
    ):
        """Initialize RAG pipeline with security and performance features.
        
        Args:
            docs_path: Path to documents directory
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            retrieval_k: Number of documents to retrieve
            embedding_model: Embedding model name
            use_vector_db: Whether to use the new VectorDB implementation
        """
        self.config = get_config()
        self.docs_path = Path(docs_path)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retrieval_k = retrieval_k
        self.embedding_model = embedding_model
        self.use_vector_db = use_vector_db and VECTOR_DB_AVAILABLE
        
        # Initialize components
        self.document_loader = SecureDocumentLoader(self.config.project_root)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.metrics = RAGMetrics()
        
        # Cache and state
        self._vector_store: Optional[VectorStore] = None
        self._vector_db: Optional[VectorDB] = None
        self._retriever: Optional[BaseRetriever] = None
        self._embeddings = None
        self._documents_cache = {}
        self._vector_store_lock = RLock()
        
        logging.info(f"RAG Pipeline initialized for: {self.docs_path}, using VectorDB: {self.use_vector_db}")
    
    @lru_cache(maxsize=1)
    def _get_embeddings(self):
        """Get embedding model with caching."""
        try:
            return HuggingFaceEmbeddings(
                model_name=self.embedding_model,
                cache_folder=str(self.config.project_root / '.cache' / 'embeddings')
            )
        except Exception as e:
            logging.error(f"Failed to load embedding model {self.embedding_model}: {e}")
            raise RAGError(f"Embedding model initialization failed: {e}")
    
    def _chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks with metadata preservation."""
        chunked_docs = []
        
        for doc in documents:
            chunks = self.text_splitter.split_documents([doc])
            
            # Add chunk metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    'chunk_id': f"{doc.metadata.get('file_path', 'unknown')}_{i}",
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'source_file': doc.metadata.get('file_path', 'unknown')
                })
                chunked_docs.append(chunk)
        
        return chunked_docs
    
    @async_timed
    async def initialize_vector_store(self, force_rebuild: bool = False) -> None:
        """Initialize or rebuild the vector store asynchronously."""
        with self._vector_store_lock:
            if (self._vector_store is not None or self._vector_db is not None) and not force_rebuild:
                logging.info("Vector store already initialized")
                return
            
            logging.info("Initializing vector store...")
            start_time = time.perf_counter()
            
            try:
                # Load documents
                if self.docs_path.is_file():
                    documents = await run_in_executor(self.document_loader.load_document, self.docs_path)
                else:
                    documents = await run_in_executor(self.document_loader.load_directory, self.docs_path)
                
                if not documents:
                    raise RAGError(f"No documents found in {self.docs_path}")
                
                # Chunk documents
                chunked_docs = await run_in_executor(self._chunk_documents, documents)
                
                if self.use_vector_db:
                    # Use new VectorDB implementation
                    await self._initialize_vector_db(chunked_docs)
                else:
                    # Use legacy FAISS implementation
                    await self._initialize_legacy_vector_store(chunked_docs)
                
                # Update metrics
                self.metrics.metrics['document_count'] = len(documents)
                self.metrics.metrics['vector_store_size'] = len(chunked_docs)
                
                init_time = time.perf_counter() - start_time
                logging.info(
                    f"Vector store initialized: {len(documents)} docs, "
                    f"{len(chunked_docs)} chunks in {init_time:.2f}s"
                )
                
            except Exception as e:
                logging.error(f"Vector store initialization failed: {e}")
                raise RAGError(f"Failed to initialize vector store: {e}")
    
    async def _initialize_vector_db(self, chunked_docs: List[Document]) -> None:
        """Initialize using the new VectorDB implementation."""
        try:
            # Get VectorDB instance
            db_path = self.config.project_root / 'data' / 'rag_vector_db'
            self._vector_db = await get_vector_db(
                embedding_model=self.embedding_model,
                db_path=db_path
            )
            
            # Prepare documents for VectorDB
            doc_texts = [doc.page_content for doc in chunked_docs]
            doc_metadatas = [doc.metadata for doc in chunked_docs]
            doc_ids = [doc.metadata.get('chunk_id', f'chunk_{i}') for i, doc in enumerate(chunked_docs)]
            
            # Add documents to VectorDB
            await self._vector_db.add_documents_async(
                documents=doc_texts,
                metadatas=doc_metadatas,
                ids=doc_ids
            )
            
            logging.info(f"VectorDB initialized with {len(chunked_docs)} chunks")
            
        except Exception as e:
            logging.error(f"VectorDB initialization failed: {e}")
            # Fallback to legacy implementation
            logging.info("Falling back to legacy FAISS implementation")
            self.use_vector_db = False
            await self._initialize_legacy_vector_store(chunked_docs)
    
    async def _initialize_legacy_vector_store(self, chunked_docs: List[Document]) -> None:
        """Initialize using the legacy FAISS implementation."""
        # Get embeddings
        embeddings = await run_in_executor(self._get_embeddings)
        
        # Create vector store
        self._vector_store = await run_in_executor(
            FAISS.from_documents, 
            chunked_docs, 
            embeddings
        )
        
        # Create retriever
        self._retriever = self._vector_store.as_retriever(
            search_kwargs={"k": self.retrieval_k}
        )
        
        logging.info(f"Legacy FAISS vector store initialized with {len(chunked_docs)} chunks")
    
    @async_timed
    async def retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents for a query."""
        if self._vector_store is None and self._vector_db is None:
            await self.initialize_vector_store()
        
        self.metrics.increment_queries()
        start_time = time.perf_counter()
        
        try:
            # Check cache first
            cache_key = f"{query}_{self.retrieval_k}"
            if cache_key in self._documents_cache:
                self.metrics.increment_cache_hits()
                return self._documents_cache[cache_key]
            
            # Retrieve documents based on implementation
            if self.use_vector_db and self._vector_db:
                documents = await self._retrieve_from_vector_db(query)
            else:
                documents = await self._retrieve_from_legacy_store(query)
            
            # Cache results (limit cache size)
            if len(self._documents_cache) < 100:
                self._documents_cache[cache_key] = documents
            
            retrieval_time = time.perf_counter() - start_time
            self.metrics.record_retrieval_time(retrieval_time)
            
            logging.debug(f"Retrieved {len(documents)} documents in {retrieval_time:.3f}s")
            return documents
            
        except Exception as e:
            logging.error(f"Document retrieval failed: {e}")
            raise RAGError(f"Failed to retrieve documents: {e}")
    
    async def _retrieve_from_vector_db(self, query: str) -> List[Document]:
        """Retrieve documents using VectorDB."""
        results = await self._vector_db.search_async(query, top_k=self.retrieval_k)
        
        # Convert VectorDB results to Document objects
        documents = []
        for metadata, score in results:
            # Create Document object from metadata
            doc = Document(
                page_content=metadata.get('text', ''),
                metadata=metadata
            )
            documents.append(doc)
        
        return documents
    
    async def _retrieve_from_legacy_store(self, query: str) -> List[Document]:
        """Retrieve documents using legacy FAISS store."""
        if self._retriever is None:
            raise RAGError("Legacy retriever not initialized")
        
        documents = await run_in_executor(self._retriever.get_relevant_documents, query)
        return documents
    
    async def search_documents(
        self, 
        query: str, 
        k: Optional[int] = None
    ) -> List[Tuple[Document, float]]:
        """Search documents with similarity scores."""
        if self._vector_store is None:
            await self.initialize_vector_store()
        
        k = k or self.retrieval_k
        
        try:
            results = await run_in_executor(
                self._vector_store.similarity_search_with_score,
                query,
                k
            )
            return results
            
        except Exception as e:
            logging.error(f"Document search failed: {e}")
            raise RAGError(f"Failed to search documents: {e}")
    
    async def get_context_for_query(self, query: str) -> str:
        """Get formatted context string for a query."""
        documents = await self.retrieve_documents(query)
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get('source_file', 'Unknown')
            content = doc.page_content.strip()
            context_parts.append(f"[Source {i}: {Path(source).name}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def clear_cache(self) -> None:
        """Clear document cache and reset metrics."""
        self._documents_cache.clear()
        if hasattr(self, '_get_embeddings'):
            self._get_embeddings.cache_clear()
        logging.info("RAG caches cleared")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of RAG pipeline."""
        status = {
            'vector_store_initialized': self._vector_store is not None or self._vector_db is not None,
            'retriever_available': self._retriever is not None or self._vector_db is not None,
            'using_vector_db': self.use_vector_db,
            'vector_db_available': VECTOR_DB_AVAILABLE,
            'document_count': self.metrics.metrics['document_count'],
            'cache_size': len(self._documents_cache),
            'docs_path_exists': self.docs_path.exists(),
            'embedding_model': self.embedding_model
        }
        
        # Add VectorDB specific health info
        if self.use_vector_db and self._vector_db:
            try:
                vector_db_health = self._vector_db.health_check()
                status['vector_db_health'] = vector_db_health
                status['vector_db_stats'] = self._vector_db.get_stats()
            except Exception as e:
                status['vector_db_error'] = str(e)
        
        # Test retrieval if possible
        if status['vector_store_initialized']:
            try:
                test_docs = await self.retrieve_documents("test query")
                status['retrieval_working'] = True
                status['test_retrieval_count'] = len(test_docs)
            except Exception as e:
                status['retrieval_working'] = False
                status['retrieval_error'] = str(e)
        
        return status


class RAGASEvaluator:
    """RAGAS evaluation for RAG pipeline quality assessment."""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag_pipeline = rag_pipeline
        self.available = RAGAS_AVAILABLE
        
        if not self.available:
            logging.warning("RAGAS not available - evaluation features disabled")
    
    async def evaluate_response(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None
    ) -> Dict[str, float]:
        """Evaluate a single RAG response using RAGAS metrics."""
        if not self.available:
            return {'ragas_available': 0.0}
        
        try:
            # Prepare data for RAGAS
            data = {
                'question': [question],
                'answer': [answer],
                'contexts': [contexts]
            }
            
            if ground_truth:
                data['ground_truths'] = [ground_truth]
            
            # Create dataset
            dataset = Dataset.from_dict(data)
            
            # Define metrics
            metrics = [faithfulness, answer_relevancy, context_precision]
            if ground_truth:
                metrics.append(context_recall)
            
            # Run evaluation
            result = await run_in_executor(evaluate, dataset, metrics=metrics)
            
            # Extract scores
            scores = {}
            for metric in metrics:
                metric_name = metric.name
                if metric_name in result:
                    scores[metric_name] = float(result[metric_name])
            
            # Record metrics
            self.rag_pipeline.metrics.record_evaluation_scores(scores)
            
            return scores
            
        except Exception as e:
            logging.error(f"RAGAS evaluation failed: {e}")
            return {'evaluation_error': -1.0}
    
    async def batch_evaluate(
        self,
        evaluation_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Batch evaluate multiple RAG responses.
        
        Args:
            evaluation_data: List of dicts with keys: question, answer, contexts, ground_truth (optional)
        """
        if not self.available:
            return {'ragas_available': False, 'batch_scores': []}
        
        batch_scores = []
        
        for data in evaluation_data:
            scores = await self.evaluate_response(
                data['question'],
                data['answer'],
                data['contexts'],
                data.get('ground_truth')
            )
            batch_scores.append(scores)
        
        # Calculate aggregate metrics
        aggregate = {}
        if batch_scores:
            for metric in batch_scores[0].keys():
                values = [scores.get(metric, 0) for scores in batch_scores if metric in scores]
                if values:
                    aggregate[f'avg_{metric}'] = sum(values) / len(values)
                    aggregate[f'min_{metric}'] = min(values)
                    aggregate[f'max_{metric}'] = max(values)
        
        return {
            'ragas_available': True,
            'batch_scores': batch_scores,
            'aggregate_metrics': aggregate,
            'total_evaluations': len(batch_scores)
        }
    
    def detect_hallucination(self, answer: str, contexts: List[str], threshold: float = 0.7) -> Dict[str, Any]:
        """Simple hallucination detection based on context overlap."""
        if not contexts or not answer:
            return {'hallucination_risk': 'high', 'confidence': 0.0, 'reason': 'No context or empty answer'}
        
        # Simple word overlap check
        answer_words = set(answer.lower().split())
        context_words = set()
        for context in contexts:
            context_words.update(context.lower().split())
        
        if not context_words:
            return {'hallucination_risk': 'high', 'confidence': 0.0, 'reason': 'No context words'}
        
        overlap = len(answer_words & context_words) / len(answer_words) if answer_words else 0
        
        if overlap >= threshold:
            risk = 'low'
        elif overlap >= threshold * 0.6:
            risk = 'medium'
        else:
            risk = 'high'
        
        return {
            'hallucination_risk': risk,
            'confidence': overlap,
            'word_overlap_ratio': overlap,
            'threshold_used': threshold
        }


# Global RAG pipeline instance (initialized lazily)
_rag_pipeline: Optional[RAGPipeline] = None


async def get_rag_pipeline(docs_path: Optional[Union[str, Path]] = None) -> RAGPipeline:
    """Get or create the global RAG pipeline instance."""
    global _rag_pipeline
    
    if _rag_pipeline is None:
        if docs_path is None:
            # Default to docs directory in project root
            config = get_config()
            docs_path = config.project_root / 'docs'
        
        _rag_pipeline = RAGPipeline(docs_path)
        await _rag_pipeline.initialize_vector_store()
    
    return _rag_pipeline


# Export key classes and functions
__all__ = [
    'RAGPipeline',
    'RAGASEvaluator', 
    'RAGError',
    'RAGMetrics',
    'SecureDocumentLoader',
    'get_rag_pipeline'
]