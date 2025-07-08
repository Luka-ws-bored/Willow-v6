"""
Unit tests for the RAG Router system.

Tests the routing logic for directing queries through different processing pipelines.
Updated for LangChain-powered RAG implementation.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from willow.rag_router import RAGRouter, RouteType, IntentLevel, create_rag_config


class TestRAGRouter(unittest.TestCase):
    """Test cases for the RAG Router system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "plugin_routing": {
                "color_mood_mapper": {
                    "keywords": ["color", "mood", "emotion"],
                    "priority": 1
                },
                "bug_buster": {
                    "keywords": ["bug", "error", "debug"],
                    "priority": 2
                }
            },
            "rag": {
                "docs_path": "docs/data/",
                "model": "gpt-3.5-turbo",
                "k": 3
            }
        }
        
        # Mock LangChain components
        self.mock_embeddings = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_vector_store = MagicMock()
        self.mock_qa_chain = MagicMock()
    
    @patch('willow.rag_router.OpenAIEmbeddings')
    @patch('willow.rag_router.ChatOpenAI')
    @patch('willow.rag_router.FAISS')
    def test_router_initialization(self, mock_faiss, mock_chat_openai, mock_embeddings):
        """Test RAG router initialization with LangChain components."""
        # Setup mocks
        mock_embeddings.return_value = self.mock_embeddings
        mock_chat_openai.return_value = self.mock_llm
        mock_faiss.from_texts.return_value = self.mock_vector_store
        
        router = RAGRouter(self.config)
        
        self.assertIsInstance(router, RAGRouter)
        self.assertEqual(router.config, self.config)
        self.assertIsNotNone(router.embeddings)
        self.assertIsNotNone(router.llm)
    
    def test_route_query_basic(self):
        """Test basic query routing functionality."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test basic routing
            response = router.route_query("What is the weather like?")
            self.assertIsInstance(response, str)
    
    def test_intent_detection(self):
        """Test intent detection functionality."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test simple intent
            intent = router._detect_intent("What color represents happiness?")
            self.assertEqual(intent, IntentLevel.SIMPLE)
            
            # Test complex intent
            intent = router._detect_intent("How does the RAG system work?")
            self.assertEqual(intent, IntentLevel.COMPLEX)
            
            # Test unknown intent
            intent = router._detect_intent("Hello there")
            self.assertEqual(intent, IntentLevel.UNKNOWN)
    
    def test_route_decision(self):
        """Test route decision logic."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test plugin route
            route = router._decide_route("Test color query", IntentLevel.SIMPLE)
            self.assertEqual(route, RouteType.PLUGIN)
            
            # Test RAG route (when qa_chain is available)
            router.qa_chain = MagicMock()
            route = router._decide_route("Test complex query", IntentLevel.COMPLEX)
            self.assertEqual(route, RouteType.RAG)
            
            # Test fallback route
            router.qa_chain = None
            route = router._decide_route("Test query", IntentLevel.COMPLEX)
            self.assertEqual(route, RouteType.FALLBACK)
    
    def test_plugin_route_processing(self):
        """Test plugin route processing."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            response = router._process_plugin_route("Test plugin query", IntentLevel.SIMPLE)
            self.assertIn("PLUGIN ROUTE", response)
    
    def test_rag_route_processing(self):
        """Test RAG route processing."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test with available QA chain
            router.qa_chain = MagicMock()
            router.qa_chain.run.return_value = "RAG response"
            
            response = router._process_rag_route("Test RAG query", IntentLevel.COMPLEX)
            self.assertEqual(response, "RAG response")
            
            # Test fallback when QA chain is None
            router.qa_chain = None
            with patch.object(router, '_process_fallback_route') as mock_fallback:
                mock_fallback.return_value = "Fallback response"
                response = router._process_rag_route("Test RAG query", IntentLevel.COMPLEX)
                mock_fallback.assert_called_once()
    
    def test_fallback_route_processing(self):
        """Test fallback route processing."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test with available LLM
            router.llm = MagicMock()
            router.llm.predict.return_value = "LLM response"
            
            response = router._process_fallback_route("Test fallback query", IntentLevel.UNKNOWN)
            self.assertEqual(response, "LLM response")
            
            # Test when LLM is not available
            router.llm = None
            response = router._process_fallback_route("Test fallback query", IntentLevel.UNKNOWN)
            self.assertIn("LLM not available", response)
    
    def test_empty_query_handling(self):
        """Test handling of empty queries."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            response = router.route_query("")
            self.assertIn("Please provide a valid query", response)
            
            response = router.route_query("   ")
            self.assertIn("Please provide a valid query", response)
    
    def test_error_handling(self):
        """Test error handling and recovery."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            # Test error handling
            response = router._handle_error("Test query", Exception("Test error"))
            self.assertIn("Sorry, I encountered an error", response)
    
    def test_route_statistics(self):
        """Test route statistics tracking."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            stats = router.get_route_stats()
            self.assertIsInstance(stats, dict)
            self.assertIn("total_queries", stats)
            self.assertIn("route_distribution", stats)
            self.assertIn("rag_available", stats)
            self.assertIn("vector_store_size", stats)
    
    def test_configuration_updates(self):
        """Test dynamic configuration updates."""
        with patch.object(RAGRouter, '_initialize_rag_pipeline'):
            router = RAGRouter(self.config)
            
            new_config = {"test_setting": "test_value"}
            router.update_config(new_config)
            
            self.assertIn("test_setting", router.config)
            self.assertEqual(router.config["test_setting"], "test_value")
    
    def test_create_rag_config(self):
        """Test RAG configuration creation utility."""
        config = create_rag_config("test/path", "gpt-4", 5)
        
        self.assertIn("rag", config)
        self.assertEqual(config["rag"]["docs_path"], "test/path")
        self.assertEqual(config["rag"]["model"], "gpt-4")
        self.assertEqual(config["rag"]["k"], 5)


class TestRAGRouterIntegration(unittest.TestCase):
    """Integration tests for the RAG Router system."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create test documents directory
        os.makedirs('docs/data', exist_ok=True)
        
        # Create test document
        with open('docs/data/test_doc.txt', 'w') as f:
            f.write("This is a test document for RAG testing.")
    
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('willow.rag_router.OpenAIEmbeddings')
    @patch('willow.rag_router.ChatOpenAI')
    @patch('willow.rag_router.FAISS')
    def test_end_to_end_routing(self, mock_faiss, mock_chat_openai, mock_embeddings):
        """Test complete routing pipeline."""
        # Setup mocks
        mock_embeddings.return_value = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        mock_faiss.from_documents.return_value = MagicMock()
        mock_faiss.from_texts.return_value = MagicMock()
        
        config = {
            "rag": {
                "docs_path": "docs/data/",
                "model": "gpt-3.5-turbo",
                "k": 3
            }
        }
        
        router = RAGRouter(config)
        
        # Test end-to-end routing
        response = router.route_query("Integration test query")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
    
    @patch('willow.rag_router.OpenAIEmbeddings')
    @patch('willow.rag_router.ChatOpenAI')
    def test_document_loading(self, mock_chat_openai, mock_embeddings):
        """Test document loading functionality."""
        # Setup mocks
        mock_embeddings.return_value = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        
        config = {
            "rag": {
                "docs_path": "docs/data/",
                "model": "gpt-3.5-turbo",
                "k": 3
            }
        }
        
        with patch('willow.rag_router.FAISS') as mock_faiss:
            mock_faiss.from_documents.return_value = MagicMock()
            
            router = RAGRouter(config)
            
            # Verify document loading was attempted
            mock_faiss.from_documents.assert_called_once()


class TestRAGRouterEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    @patch('willow.rag_router.OpenAIEmbeddings')
    @patch('willow.rag_router.ChatOpenAI')
    def setUp(self, mock_chat_openai, mock_embeddings):
        """Set up edge case test fixtures."""
        mock_embeddings.return_value = MagicMock()
        mock_chat_openai.return_value = MagicMock()
        
        with patch('willow.rag_router.FAISS') as mock_faiss:
            mock_faiss.from_texts.return_value = MagicMock()
            self.router = RAGRouter()
    
    def test_very_long_query(self):
        """Test handling of very long queries."""
        long_query = "A" * 10000  # Very long query
        response = self.router.route_query(long_query)
        self.assertIsInstance(response, str)
    
    def test_special_characters(self):
        """Test handling of special characters in queries."""
        special_query = "Test query with special chars: <>&\"'"
        response = self.router.route_query(special_query)
        self.assertIsInstance(response, str)
    
    def test_unicode_characters(self):
        """Test handling of unicode characters in queries."""
        unicode_query = "Test query with unicode: 🚀🌟✨"
        response = self.router.route_query(unicode_query)
        self.assertIsInstance(response, str)


if __name__ == '__main__':
    unittest.main() 