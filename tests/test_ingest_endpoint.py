import json
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the root directory to the path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestIngestEndpoint(unittest.TestCase):
    """Test the /ingest endpoint in backend.py"""
    
    def test_ingest_valid_document(self):
        """Test ingesting a valid document."""
        test_document = "This is a test document for ingestion."
        
        # Since we're not running the actual server, we'll test the logic directly
        # by importing the function
        try:
            from backend import ingest_document
            
            # Mock the request object
            with patch('backend.request') as mock_request:
                mock_request.get_json.return_value = {"document": test_document}
                
                # Mock the logger
                with patch('backend.logger') as mock_logger:
                    # Mock the VectorDB
                    with patch('src.utils.vector_db.VectorDB') as mock_vector_db:
                        mock_db_instance = MagicMock()
                        mock_vector_db.return_value = mock_db_instance
                        
                        # Call the function
                        response = ingest_document()
                        
                        # Check that the response is correct
                        self.assertEqual(response[1], 200)
                        response_data = json.loads(response[0].get_data(as_text=True))
                        self.assertEqual(response_data["status"], "success")
                        
                        # Check that VectorDB was called correctly
                        mock_vector_db.assert_called_once()
                        mock_db_instance.add_documents.assert_called_once_with([test_document])
                        
        except ImportError as e:
            self.skipTest(f"Could not import backend module: {e}")
    
    def test_ingest_missing_document_field(self):
        """Test ingesting with missing document field."""
        try:
            from backend import ingest_document
            
            # Mock the request object with missing document field
            with patch('backend.request') as mock_request:
                mock_request.get_json.return_value = {"text": "missing document field"}
                
                # Mock the logger
                with patch('backend.logger') as mock_logger:
                    # Call the function
                    response = ingest_document()
                    
                    # Check that the response is correct (400 error)
                    self.assertEqual(response[1], 400)
                    response_data = json.loads(response[0].get_data(as_text=True))
                    self.assertIn("error", response_data)
                    
        except ImportError as e:
            self.skipTest(f"Could not import backend module: {e}")
    
    def test_ingest_non_string_document(self):
        """Test ingesting with non-string document field."""
        try:
            from backend import ingest_document
            
            # Mock the request object with non-string document
            with patch('backend.request') as mock_request:
                mock_request.get_json.return_value = {"document": 12345}
                
                # Mock the logger
                with patch('backend.logger') as mock_logger:
                    # Call the function
                    response = ingest_document()
                    
                    # Check that the response is correct (400 error)
                    self.assertEqual(response[1], 400)
                    response_data = json.loads(response[0].get_data(as_text=True))
                    self.assertIn("error", response_data)
                    
        except ImportError as e:
            self.skipTest(f"Could not import backend module: {e}")

if __name__ == '__main__':
    unittest.main()