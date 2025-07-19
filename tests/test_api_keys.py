#!/usr/bin/env python3
"""
Test script to verify API keys are working properly.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from willow.rag_router import RAGRouter


def test_api_keys():
    """Test that API keys are working."""
    print("Testing API keys...")
    
    # Check environment variables
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")
    
    print(f"OpenRouter API Key: {'✓ Set' if openrouter_key else '✗ Not set'}")
    print(f"Gemini API Key: {'✓ Set' if gemini_key else '✗ Not set'}")
    print(f"OpenAI API Key: {'✓ Set' if openai_key else '✗ Not set'}")
    print(f"Hugging Face API Key: {'✓ Set' if huggingface_key else '✗ Not set'}")
    
    if not any([openrouter_key, gemini_key, openai_key, huggingface_key]):
        print("Error: No API keys found!")
        return False
    
    # Test RAG router initialization
    try:
        print("\nInitializing RAG Router...")
        rag = RAGRouter()
        
        # Check providers
        provider_count = len(rag.providers)
        print(f"Providers initialized: {provider_count}")
        
        for name, client in rag.providers:
            print(f"  - {name}: ✓")
        
        if provider_count == 0:
            print("Warning: No providers initialized!")
            return False
        
        # Test a simple query
        print("\nTesting simple query...")
        test_query = "What is the meaning of life?"
        response = rag.route_query(test_query)
        
        print(f"Query: {test_query}")
        print(f"Response: {response[:200]}...")
        
        if response.startswith("[FALLBACK ERROR]"):
            print("Error: All providers failed!")
            return False
        
        print("✓ API keys test passed!")
        return True
        
    except Exception as e:
        print(f"Error testing API keys: {e}")
        return False


if __name__ == "__main__":
    success = test_api_keys()
    sys.exit(0 if success else 1) 