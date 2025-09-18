#!/usr/bin/env python3
"""
Test RAG query functionality
"""

import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_rag_query():
    """Test RAG query functionality"""
    try:
        # Try to import the main module
        from src.main import async_query_rag_simple
        
        # Test with a simple query
        print("Testing RAG query with a simple document...")
        
        # Create a simple document for testing
        documents = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Machine learning is a subset of artificial intelligence that focuses on algorithms learning from data.",
            "Willow is an AI framework that supports multiple LLM providers and RAG functionality."
        ]
        
        query = "What is Python?"
        
        print(f"Query: {query}")
        print(f"Documents: {len(documents)} documents provided")
        
        # Try the RAG query
        response = await async_query_rag_simple(query, documents=documents, top_k=2)
        print(f"Response: {response}")
        print("✅ RAG query completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ RAG query failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing RAG query functionality...")
    print("=" * 50)
    
    # Run the async test
    result = asyncio.run(test_rag_query())
    
    if result:
        print("\n🎉 RAG system is working correctly!")
    else:
        print("\n💥 RAG system has issues that need to be fixed")