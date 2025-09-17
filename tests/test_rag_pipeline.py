"""
Comprehensive unit tests for RAG pipeline implementation.
Tests retrieval accuracy, response augmentation, hallucination detection, and async execution.
"""

import asyncio
import logging
import os
import tempfile
import unittest
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest


class TestRAGPipelineCore(unittest.TestCase):
    """Core tests for RAG pipeline functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_docs_path = Path(self.test_dir) / "docs"
        self.test_docs_path.mkdir(exist_ok=True)
        
        # Create test documents
        self.sample_doc1 = self.test_docs_path / "doc1.txt"
        self.sample_doc2 = self.test_docs_path / "doc2.txt"
        
        self.sample_doc1.write_text("Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.")
        self.sample_doc2.write_text("Machine learning is a subset of artificial intelligence that focuses on creating algorithms that can learn from data without being explicitly programmed.")
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)


class TestSecureDocumentLoader(TestRAGPipelineCore):
    """Tests for secure document loading functionality."""
    
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_load_single_document_success(self, mock_get_file_ops):
        """Test successful loading of a single document."""
        from src.utils.rag_pipeline import SecureDocumentLoader
        
        # Mock file operations
        mock_file_ops = Mock()
        mock_file_ops.validate_path.return_value = self.sample_doc1
        mock_get_file_ops.return_value = mock_file_ops
        
        loader = SecureDocumentLoader(Path(self.test_dir))
        documents = loader.load_document(self.sample_doc1)
        
        self.assertGreater(len(documents), 0)
        self.assertIn("Python", documents[0].page_content)
        self.assertEqual(documents[0].metadata['file_path'], str(self.sample_doc1))
    
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_load_document_file_not_found(self, mock_get_file_ops):
        """Test loading non-existent document raises error."""
        from src.utils.rag_pipeline import SecureDocumentLoader, RAGError
        
        non_existent_path = Path(self.test_dir) / "nonexistent.txt"
        
        mock_file_ops = Mock()
        mock_file_ops.validate_path.return_value = non_existent_path
        mock_get_file_ops.return_value = mock_file_ops
        
        loader = SecureDocumentLoader(Path(self.test_dir))
        
        with self.assertRaises(RAGError):
            loader.load_document(non_existent_path)
    
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_load_directory_success(self, mock_get_file_ops):
        """Test successful loading of directory documents."""
        from src.utils.rag_pipeline import SecureDocumentLoader
        
        mock_file_ops = Mock()
        mock_file_ops.validate_path.return_value = self.test_docs_path
        mock_file_ops.list_safe_files.return_value = [self.sample_doc1, self.sample_doc2]
        mock_get_file_ops.return_value = mock_file_ops
        
        loader = SecureDocumentLoader(Path(self.test_dir))
        documents = loader.load_directory(self.test_docs_path)
        
        self.assertGreater(len(documents), 0)
        doc_contents = [doc.page_content for doc in documents]
        self.assertTrue(any("Python" in content for content in doc_contents))
        self.assertTrue(any("Machine learning" in content for content in doc_contents))


class TestRAGMetrics(TestRAGPipelineCore):
    """Tests for RAG metrics collection and reporting."""
    
    def test_metrics_initialization(self):
        """Test metrics object initialization."""
        from src.utils.rag_pipeline import RAGMetrics
        
        metrics = RAGMetrics()
        summary = metrics.get_summary()
        
        self.assertEqual(summary['total_queries'], 0)
        self.assertEqual(summary['cache_hits'], 0)
        self.assertEqual(len(summary['retrieval_time']), 0)
    
    def test_metrics_recording(self):
        """Test recording various metrics."""
        from src.utils.rag_pipeline import RAGMetrics
        
        metrics = RAGMetrics()
        
        # Record some metrics
        metrics.record_retrieval_time(0.5)
        metrics.record_generation_time(1.2)
        metrics.increment_queries()
        metrics.increment_cache_hits()
        
        summary = metrics.get_summary()
        
        self.assertEqual(summary['total_queries'], 1)
        self.assertEqual(summary['cache_hits'], 1)
        self.assertEqual(summary['cache_hit_rate'], 1.0)
        self.assertEqual(summary['avg_retrieval_time'], 0.5)
        self.assertEqual(summary['avg_generation_time'], 1.2)
    
    def test_evaluation_scores_recording(self):
        """Test recording RAGAS evaluation scores."""
        from src.utils.rag_pipeline import RAGMetrics
        
        metrics = RAGMetrics()
        test_scores = {
            'faithfulness': 0.85,
            'answer_relevancy': 0.90,
            'context_precision': 0.78
        }
        
        metrics.record_evaluation_scores(test_scores)
        summary = metrics.get_summary()
        
        self.assertEqual(summary['avg_faithfulness'], 0.85)
        self.assertEqual(summary['avg_answer_relevancy'], 0.90)
        self.assertEqual(summary['avg_context_precision'], 0.78)


class TestRAGPipelineAsync(TestRAGPipelineCore):
    """Async tests for RAG pipeline."""
    
    def setUp(self):
        """Set up async test environment."""
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up async test environment."""
        super().tearDown()
        self.loop.close()
    
    @patch('src.utils.rag_pipeline.get_config')
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_rag_pipeline_initialization(self, mock_get_file_ops, mock_get_config):
        """Test RAG pipeline initialization."""
        from src.utils.rag_pipeline import RAGPipeline
        
        # Mock configuration
        mock_config = Mock()
        mock_config.project_root = Path(self.test_dir)
        mock_get_config.return_value = mock_config
        
        mock_file_ops = Mock()
        mock_get_file_ops.return_value = mock_file_ops
        
        rag_pipeline = RAGPipeline(
            docs_path=self.test_docs_path,
            chunk_size=100,
            chunk_overlap=20,
            retrieval_k=3
        )
        
        self.assertEqual(rag_pipeline.docs_path, self.test_docs_path)
        self.assertEqual(rag_pipeline.chunk_size, 100)
        self.assertEqual(rag_pipeline.retrieval_k, 3)
        self.assertIsNotNone(rag_pipeline.metrics)
    
    @patch('src.utils.rag_pipeline.HuggingFaceEmbeddings')
    @patch('src.utils.rag_pipeline.FAISS')
    @patch('src.utils.rag_pipeline.get_config')
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_vector_store_initialization_async(self, mock_get_file_ops, mock_get_config, mock_faiss, mock_embeddings):
        """Test async vector store initialization."""
        from src.utils.rag_pipeline import RAGPipeline
        
        # Mock configuration
        mock_config = Mock()
        mock_config.project_root = Path(self.test_dir)
        mock_get_config.return_value = mock_config
        
        mock_file_ops = Mock()
        mock_get_file_ops.return_value = mock_file_ops
        
        # Mock embeddings and FAISS
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        mock_faiss.from_documents.return_value = mock_vector_store
        
        rag_pipeline = RAGPipeline(docs_path=self.test_docs_path)
        
        # Mock document loader methods
        with patch.object(rag_pipeline.document_loader, 'load_directory') as mock_load_dir:
            mock_load_dir.return_value = [Mock(page_content="Test content", metadata={'file_path': 'test.txt'})]
            
            async def run_test():
                await rag_pipeline.initialize_vector_store()
                self.assertIsNotNone(rag_pipeline._vector_store)
                self.assertIsNotNone(rag_pipeline._retriever)
            
            self.loop.run_until_complete(run_test())
    
    @patch('src.utils.rag_pipeline.get_config')
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_health_check_async(self, mock_get_file_ops, mock_get_config):
        """Test async health check functionality."""
        from src.utils.rag_pipeline import RAGPipeline
        
        # Mock configuration
        mock_config = Mock()
        mock_config.project_root = Path(self.test_dir)
        mock_get_config.return_value = mock_config
        
        mock_file_ops = Mock()
        mock_get_file_ops.return_value = mock_file_ops
        
        rag_pipeline = RAGPipeline(docs_path=self.test_docs_path)
        
        async def run_test():
            health_status = await rag_pipeline.health_check()
            
            self.assertIn('vector_store_initialized', health_status)
            self.assertIn('docs_path_exists', health_status)
            self.assertIn('embedding_model', health_status)
            self.assertEqual(health_status['docs_path_exists'], True)
        
        self.loop.run_until_complete(run_test())


class TestRAGASEvaluator(TestRAGPipelineCore):
    """Tests for RAGAS evaluation functionality."""
    
    @patch('src.utils.rag_pipeline.RAGAS_AVAILABLE', True)
    @patch('src.utils.rag_pipeline.evaluate')
    @patch('src.utils.rag_pipeline.Dataset')
    def test_evaluate_response_success(self, mock_dataset, mock_evaluate):
        """Test successful response evaluation."""
        from src.utils.rag_pipeline import RAGASEvaluator, RAGPipeline
        
        # Mock RAG pipeline
        mock_rag_pipeline = Mock(spec=RAGPipeline)
        mock_rag_pipeline.metrics = Mock()
        mock_rag_pipeline.metrics.record_evaluation_scores = Mock()
        
        # Mock RAGAS components
        mock_dataset_instance = Mock()
        mock_dataset.from_dict.return_value = mock_dataset_instance
        
        mock_evaluate.return_value = {
            'faithfulness': 0.85,
            'answer_relevancy': 0.90,
            'context_precision': 0.78
        }
        
        evaluator = RAGASEvaluator(mock_rag_pipeline)
        
        async def run_test():
            scores = await evaluator.evaluate_response(
                question="What is Python?",
                answer="Python is a programming language.",
                contexts=["Python is a high-level programming language."]
            )
            
            self.assertIn('faithfulness', scores)
            self.assertIn('answer_relevancy', scores)
            self.assertEqual(scores['faithfulness'], 0.85)
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())
        loop.close()
    
    @patch('src.utils.rag_pipeline.RAGAS_AVAILABLE', False)
    def test_evaluate_response_ragas_unavailable(self):
        """Test evaluation when RAGAS is not available."""
        from src.utils.rag_pipeline import RAGASEvaluator, RAGPipeline
        
        mock_rag_pipeline = Mock(spec=RAGPipeline)
        evaluator = RAGASEvaluator(mock_rag_pipeline)
        
        async def run_test():
            scores = await evaluator.evaluate_response(
                question="Test question",
                answer="Test answer",
                contexts=["Test context"]
            )
            
            self.assertEqual(scores['ragas_available'], 0.0)
        
        loop = asyncio.new_event_loop()
        loop.run_until_complete(run_test())
        loop.close()
    
    def test_hallucination_detection(self):
        """Test hallucination detection functionality."""
        from src.utils.rag_pipeline import RAGASEvaluator, RAGPipeline
        
        mock_rag_pipeline = Mock(spec=RAGPipeline)
        evaluator = RAGASEvaluator(mock_rag_pipeline)
        
        # Test high overlap (low hallucination risk)
        result_low_risk = evaluator.detect_hallucination(
            answer="Python is a programming language",
            contexts=["Python is a high-level programming language known for simplicity"],
            threshold=0.5
        )
        self.assertEqual(result_low_risk['hallucination_risk'], 'low')
        
        # Test low overlap (high hallucination risk)
        result_high_risk = evaluator.detect_hallucination(
            answer="Java is the best database system",
            contexts=["Python is a programming language"],
            threshold=0.5
        )
        self.assertEqual(result_high_risk['hallucination_risk'], 'high')
        
        # Test empty context
        result_empty = evaluator.detect_hallucination(
            answer="Some answer",
            contexts=[],
            threshold=0.5
        )
        self.assertEqual(result_empty['hallucination_risk'], 'high')


class TestMainIntegration(unittest.TestCase):
    """Tests for main.py RAG integration."""
    
    def setUp(self):
        """Set up test environment for main.py integration."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up async test environment."""
        self.loop.close()
    
    @patch('src.main.get_rag_pipeline')
    @patch('src.main.async_query_llm')
    @patch('src.main.validate_prompt')
    def test_async_query_rag_success(self, mock_validate, mock_async_llm, mock_get_rag):
        """Test successful RAG query integration."""
        from src.main import async_query_rag
        
        # Mock validation
        mock_validate.return_value = True
        
        # Mock RAG pipeline
        mock_pipeline = AsyncMock()
        mock_pipeline.get_context_for_query.return_value = "Python is a programming language."
        mock_get_rag.return_value = mock_pipeline
        
        # Mock LLM response
        mock_async_llm.return_value = "Based on the context, Python is indeed a programming language known for its simplicity."
        
        async def run_test():
            response = await async_query_rag("What is Python?")
            self.assertIn("Python", response)
            mock_get_rag.assert_called_once()
            mock_pipeline.get_context_for_query.assert_called_once_with("What is Python?")
        
        self.loop.run_until_complete(run_test())
    
    @patch('src.main.get_rag_pipeline')
    @patch('src.main.async_query_llm')
    @patch('src.main.validate_prompt')
    def test_async_query_rag_fallback(self, mock_validate, mock_async_llm, mock_get_rag):
        """Test RAG fallback to standard LLM."""
        from src.main import async_query_rag
        from src.utils.rag_pipeline import RAGError
        
        # Mock validation
        mock_validate.return_value = True
        
        # Mock RAG pipeline failure
        mock_get_rag.side_effect = RAGError("Pipeline failed")
        
        # Mock LLM response
        mock_async_llm.return_value = "Standard LLM response"
        
        async def run_test():
            response = await async_query_rag("What is Python?")
            self.assertEqual(response, "Standard LLM response")
            mock_async_llm.assert_called_once_with("What is Python?")
        
        self.loop.run_until_complete(run_test())
    
    @patch('src.main.async_query_rag')
    def test_batch_query_rag(self, mock_async_rag):
        """Test batch RAG query processing."""
        from src.main import batch_query_rag
        
        # Mock individual RAG responses
        mock_async_rag.side_effect = [
            "Response 1",
            "Response 2", 
            Exception("Error in response 3")
        ]
        
        prompts = ["Query 1", "Query 2", "Query 3"]
        
        async def run_test():
            responses = await batch_query_rag(prompts)
            
            self.assertEqual(len(responses), 3)
            self.assertEqual(responses[0], "Response 1")
            self.assertEqual(responses[1], "Response 2")
            self.assertIn("Error processing prompt 3", responses[2])
        
        self.loop.run_until_complete(run_test())


class TestPerformanceAndSecurity(TestRAGPipelineCore):
    """Tests for performance optimization and security features."""
    
    @patch('src.utils.rag_pipeline.get_config')
    @patch('src.utils.rag_pipeline.get_file_ops') 
    def test_cache_functionality(self, mock_get_file_ops, mock_get_config):
        """Test caching mechanisms in RAG pipeline."""
        from src.utils.rag_pipeline import RAGPipeline
        
        # Mock configuration
        mock_config = Mock()
        mock_config.project_root = Path(self.test_dir)
        mock_get_config.return_value = mock_config
        
        mock_file_ops = Mock()
        mock_get_file_ops.return_value = mock_file_ops
        
        rag_pipeline = RAGPipeline(docs_path=self.test_docs_path)
        
        # Test cache clearing
        rag_pipeline._documents_cache = {"test_key": "test_value"}
        self.assertEqual(len(rag_pipeline._documents_cache), 1)
        
        rag_pipeline.clear_cache()
        self.assertEqual(len(rag_pipeline._documents_cache), 0)
    
    @patch('src.utils.rag_pipeline.get_file_ops')
    def test_secure_document_loading(self, mock_get_file_ops):
        """Test security features in document loading."""
        from src.utils.rag_pipeline import SecureDocumentLoader, RAGError
        
        mock_file_ops = Mock()
        mock_file_ops.validate_path.side_effect = lambda x: Path(x)
        mock_get_file_ops.return_value = mock_file_ops
        
        loader = SecureDocumentLoader(Path(self.test_dir))
        
        # Test loading from a secure path
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'is_file', return_value=True):
            
            with patch('src.utils.rag_pipeline.TextLoader') as mock_text_loader:
                mock_loader_instance = Mock()
                mock_document = Mock()
                mock_document.metadata = {}
                mock_document.page_content = "Test content"
                mock_loader_instance.load.return_value = [mock_document]
                mock_text_loader.return_value = mock_loader_instance
                
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 1024
                    mock_stat.return_value.st_mtime = 1234567890
                    
                    documents = loader.load_document("/safe/path/document.txt")
                    self.assertEqual(len(documents), 1)
                    self.assertIn('file_size', documents[0].metadata)


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run all tests
    unittest.main(verbosity=2)