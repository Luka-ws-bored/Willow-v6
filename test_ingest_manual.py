#!/usr/bin/env python3
"""
Manual test script for the /ingest endpoint.
This script tests the ingest functionality without requiring a running server.
"""

import sys
import os
import json

# Add the root directory to the path so we can import backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ingest_function():
    """Test the ingest_document function directly."""
    print("Testing ingest_document function...")
    
    try:
        from backend import ingest_document
        
        # Create a mock request object
        class MockRequest:
            def get_json(self):
                return {"document": "This is a test document for ingestion."}
        
        # Create a mock response object
        class MockResponse:
            def __init__(self, data, status_code):
                self.data = data
                self.status_code = status_code
                
            def get_data(self, as_text=True):
                if as_text:
                    return json.dumps(self.data)
                return self.data
        
        # Mock the Flask request and jsonify functions
        import backend
        original_request = backend.request
        original_jsonify = backend.jsonify
        
        # Replace with mocks
        backend.request = MockRequest()
        backend.jsonify = lambda *args, **kwargs: MockResponse(args[0] if args else kwargs, 200)
        
        # Mock the logger
        import logging
        original_logger = backend.logger
        backend.logger = logging.getLogger(__name__)
        
        # Mock the VectorDB
        import src.utils.vector_db
        original_vector_db = src.utils.vector_db.VectorDB
        
        class MockVectorDB:
            def __init__(self):
                pass
                
            def add_documents(self, docs):
                print(f"Mock VectorDB.add_documents called with {len(docs)} documents")
                # Verify the document was passed correctly
                assert len(docs) == 1
                assert docs[0] == "This is a test document for ingestion."
                print("✓ Document correctly passed to VectorDB")
        
        src.utils.vector_db.VectorDB = MockVectorDB
        
        try:
            # Call the function
            response = ingest_document()
            
            # Check the response
            print(f"Response status code: {response[1]}")
            response_data = json.loads(response[0].get_data(as_text=True))
            print(f"Response data: {response_data}")
            
            if response[1] == 200 and response_data.get("status") == "success":
                print("✓ Test passed: Document ingestion successful")
                return True
            else:
                print("✗ Test failed: Unexpected response")
                return False
                
        finally:
            # Restore original functions
            backend.request = original_request
            backend.jsonify = original_jsonify
            backend.logger = original_logger
            src.utils.vector_db.VectorDB = original_vector_db
            
    except Exception as e:
        print(f"✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running manual test for /ingest endpoint...")
    success = test_ingest_function()
    if success:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)