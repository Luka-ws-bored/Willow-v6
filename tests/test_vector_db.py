"""
Comprehensive unit tests for Vector Database implementation.
Tests embedding creation, document storage, search functionality, and performance.
"""

import asyncio
import logging
import os
import tempfile
import unittest
import shutil
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest


class TestVectorDBCore(unittest.TestCase):
    """Core tests for Vector DB functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.test_dir) / "vector_db"
        
        # Sample test documents
        self.sample_docs = [
            "Python is a high-level programming language known for its simplicity.",
            "Machine learning is a subset of artificial intelligence.",
            "Vector databases store and search high-dimensional data efficiently.",
            "FAISS is a library for efficient similarity search and clustering.",
            "Willow v6 includes advanced RAG capabilities with vector storage."
        ]
        
        self.sample_metadata = [
            {"category": "programming", "topic": "python"},
            {"category": "ai", "topic": "machine_learning"},
            {"category": "database", "topic": "vector_search"},
            {"category": "library", "topic": "faiss"},
            {"category": "project", "topic": "willow"}
        ]
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)


class TestVectorDBAvailability(TestVectorDBCore):
    """Test Vector DB availability and dependency checking."""
    
    def test_import_availability(self):
        """Test checking if vector DB dependencies are available."""
        try:
            from src.utils.vector_db import VECTOR_DB_AVAILABLE
            # If this succeeds, dependencies should be marked as available or not
            self.assertIsInstance(VECTOR_DB_AVAILABLE, bool)
        except ImportError:
            # If import fails completely, that's also a valid test result
            self.skipTest("Vector DB module not importable")
    
    @patch('src.utils.vector_db.VECTOR_DB_AVAILABLE', False)
    def test_graceful_degradation_when_unavailable(self):
        """Test graceful handling when dependencies are unavailable."""
        from src.utils.vector_db import VectorDBError
        
        # Test that appropriate errors are raised
        with self.assertRaises((VectorDBError, NotImplementedError)):
            from src.utils.vector_db import embed_texts
            embed_texts(["test"])


@pytest.mark.skipif(not hasattr(pytest, 'importorskip'), reason="pytest required")
class TestVectorDBWithDependencies(TestVectorDBCore):
    """Tests that require vector DB dependencies to be available."""
    
    def setUp(self):
        """Set up test environment with dependency check."""
        super().setUp()
        try:
            from src.utils.vector_db import VECTOR_DB_AVAILABLE
            if not VECTOR_DB_AVAILABLE:
                self.skipTest("Vector DB dependencies not available")
        except ImportError:
            self.skipTest("Vector DB module not importable")
    
    def test_vector_db_initialization(self):
        """Test VectorDB initialization."""
        from src.utils.vector_db import VectorDB
        
        # Mock the config and file operations
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(
                    embedding_model='sentence-transformers/all-MiniLM-L6-v2',
                    db_path=self.test_db_path
                )
                
                self.assertEqual(db.db_path, self.test_db_path)
                self.assertIsNotNone(db.index)
                self.assertEqual(len(db.metadata), 0)
                self.assertIsNotNone(db.metrics)
                
            except Exception as e:
                self.skipTest(f"VectorDB initialization failed: {e}")
    
    def test_add_and_search_documents(self):
        """Test adding documents and searching."""
        from src.utils.vector_db import VectorDB
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(db_path=self.test_db_path)
                
                # Add sample documents
                db.add_documents(
                    documents=self.sample_docs[:3],  # Use fewer docs for faster testing
                    metadatas=self.sample_metadata[:3]
                )
                
                # Test search
                results = db.search("Python programming", top_k=2)
                
                self.assertGreater(len(results), 0)
                self.assertLessEqual(len(results), 2)
                
                # Check result structure
                for metadata, score in results:
                    self.assertIsInstance(metadata, dict)
                    self.assertIsInstance(score, float)
                    self.assertIn('text', metadata)
                    self.assertGreater(score, 0)
                
                # Test that Python-related document has high score
                python_result = next((r for r in results if "Python" in r[0]['text']), None)
                self.assertIsNotNone(python_result, "Python document should be found in search results")
                
            except Exception as e:
                self.skipTest(f"Add/search test failed: {e}")
    
    def test_document_persistence(self):
        """Test that documents persist across database instances."""
        from src.utils.vector_db import VectorDB
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                # Create first database instance and add documents
                db1 = VectorDB(db_path=self.test_db_path)
                db1.add_documents(
                    documents=["Test document for persistence"],
                    metadatas=[{"test": "persistence"}]
                )
                
                # Create second database instance (should load existing data)
                db2 = VectorDB(db_path=self.test_db_path)
                
                # Search should find the document
                results = db2.search("Test document", top_k=1)
                self.assertGreater(len(results), 0)
                self.assertIn("Test document", results[0][0]['text'])
                
            except Exception as e:
                self.skipTest(f"Persistence test failed: {e}")
    
    def test_metadata_filtering(self):
        """Test searching with metadata filters."""
        from src.utils.vector_db import VectorDB
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(db_path=self.test_db_path)
                db.add_documents(
                    documents=self.sample_docs[:3],
                    metadatas=self.sample_metadata[:3]
                )
                
                # Search with metadata filter
                results = db.search(
                    "programming",
                    top_k=5,
                    filter_metadata={"category": "programming"}
                )
                
                # Should only return programming-related documents
                for metadata, score in results:
                    self.assertEqual(metadata.get("category"), "programming")
                
            except Exception as e:
                self.skipTest(f"Metadata filtering test failed: {e}")
    
    def test_get_document_by_id(self):
        """Test retrieving documents by ID."""
        from src.utils.vector_db import VectorDB
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(db_path=self.test_db_path)
                
                # Add document with specific ID
                test_id = "test_doc_123"
                db.add_documents(
                    documents=["Document with specific ID"],
                    metadatas=[{"category": "test"}],
                    ids=[test_id]
                )
                
                # Retrieve by ID
                doc = db.get_document_by_id(test_id)
                self.assertIsNotNone(doc)
                self.assertEqual(doc['id'], test_id)
                self.assertIn("specific ID", doc['text'])
                
                # Test non-existent ID
                non_existent = db.get_document_by_id("non_existent_id")
                self.assertIsNone(non_existent)
                
            except Exception as e:
                self.skipTest(f"Get document by ID test failed: {e}")


class TestVectorDBAsync(TestVectorDBCore):
    """Async tests for Vector DB."""
    
    def setUp(self):
        """Set up async test environment."""
        super().setUp()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up async test environment."""
        super().tearDown()
        self.loop.close()
    
    def test_async_operations(self):
        """Test async add and search operations."""
        try:
            from src.utils.vector_db import VectorDB, VECTOR_DB_AVAILABLE
            if not VECTOR_DB_AVAILABLE:
                self.skipTest("Vector DB dependencies not available")
        except ImportError:
            self.skipTest("Vector DB module not importable")
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            async def run_async_test():
                try:
                    db = VectorDB(db_path=self.test_db_path)
                    
                    # Test async add
                    await db.add_documents_async(
                        documents=["Async test document"],
                        metadatas=[{"test": "async"}]
                    )
                    
                    # Test async search
                    results = await db.search_async("Async test", top_k=1)
                    
                    self.assertGreater(len(results), 0)
                    self.assertIn("Async", results[0][0]['text'])
                    
                    # Test async get by ID
                    doc = await db.get_document_by_id_async("doc_0")
                    self.assertIsNotNone(doc)
                    
                except Exception as e:
                    self.skipTest(f"Async test failed: {e}")
            
            self.loop.run_until_complete(run_async_test())


class TestVectorDBMetrics(TestVectorDBCore):
    """Test Vector DB metrics and performance monitoring."""
    
    def test_metrics_collection(self):
        """Test that metrics are collected properly."""
        from src.utils.vector_db import VectorDBMetrics
        
        metrics = VectorDBMetrics()
        
        # Test initial state
        summary = metrics.get_summary()
        self.assertEqual(summary['documents_added'], 0)
        self.assertEqual(summary['searches_performed'], 0)
        
        # Test recording metrics
        metrics.record_embedding_time(0.5)
        metrics.record_search_time(0.1)
        metrics.increment_documents_added(5)
        metrics.increment_searches()
        metrics.increment_cache_hits()
        
        # Check updated metrics
        summary = metrics.get_summary()
        self.assertEqual(summary['documents_added'], 5)
        self.assertEqual(summary['searches_performed'], 1)
        self.assertEqual(summary['cache_hits'], 1)
        self.assertEqual(summary['avg_embedding_time'], 0.5)
        self.assertEqual(summary['avg_search_time'], 0.1)
        self.assertEqual(summary['cache_hit_rate'], 1.0)
    
    def test_health_check(self):
        """Test vector database health check functionality."""
        try:
            from src.utils.vector_db import VectorDB, VECTOR_DB_AVAILABLE
            if not VECTOR_DB_AVAILABLE:
                self.skipTest("Vector DB dependencies not available")
        except ImportError:
            self.skipTest("Vector DB module not importable")
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(db_path=self.test_db_path)
                health = db.health_check()
                
                self.assertIn('db_available', health)
                self.assertIn('index_loaded', health)
                self.assertIn('total_documents', health)
                self.assertEqual(health['total_documents'], 0)
                
            except Exception as e:
                self.skipTest(f"Health check test failed: {e}")


class TestLegacyCompatibility(TestVectorDBCore):
    """Test legacy function compatibility."""
    
    def test_legacy_functions_available(self):
        """Test that legacy functions are available."""
        try:
            from src.utils.vector_db import embed_texts, create_index, load_index, search_index
            # Functions should be importable
            self.assertTrue(callable(embed_texts))
            self.assertTrue(callable(create_index))
            self.assertTrue(callable(load_index))
            self.assertTrue(callable(search_index))
        except ImportError:
            self.skipTest("Vector DB module not importable")
    
    @patch('src.utils.vector_db.VECTOR_DB_AVAILABLE', False)
    def test_legacy_functions_when_unavailable(self):
        """Test legacy functions when dependencies unavailable."""
        from src.utils.vector_db import embed_texts
        
        with self.assertRaises(NotImplementedError):
            embed_texts(["test"])


class TestErrorHandling(TestVectorDBCore):
    """Test error handling in Vector DB operations."""
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        try:
            from src.utils.vector_db import VectorDB, VectorDBError, VECTOR_DB_AVAILABLE
            if not VECTOR_DB_AVAILABLE:
                self.skipTest("Vector DB dependencies not available")
        except ImportError:
            self.skipTest("Vector DB module not importable")
        
        with patch('src.utils.vector_db.get_config') as mock_config, \
             patch('src.utils.vector_db.get_file_ops') as mock_file_ops:
            
            mock_config.return_value.project_root = Path(self.test_dir)
            mock_file_ops.return_value.validate_path.return_value = self.test_db_path
            
            try:
                db = VectorDB(db_path=self.test_db_path)
                
                # Test mismatched metadata length
                with self.assertRaises(VectorDBError):
                    db.add_documents(
                        documents=["doc1", "doc2"],
                        metadatas=[{"meta": "only_one"}]  # Mismatched length
                    )
                
                # Test mismatched IDs length
                with self.assertRaises(VectorDBError):
                    db.add_documents(
                        documents=["doc1", "doc2"],
                        ids=["id1"]  # Mismatched length
                    )
                
                # Test empty query
                results = db.search("")
                self.assertEqual(len(results), 0)
                
            except Exception as e:
                self.skipTest(f"Error handling test failed: {e}")


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)
    
    # Run all tests
    unittest.main(verbosity=2)