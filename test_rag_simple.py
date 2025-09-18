#!/usr/bin/env python3
"""
Simple test script to verify RAG system functionality
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_rag_imports():
    """Test if RAG dependencies can be imported"""
    try:
        import faiss
        print("✅ FAISS imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FAISS: {e}")
        return False
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Sentence Transformers: {e}")
        return False
    
    try:
        import langchain
        print("✅ LangChain imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LangChain: {e}")
        return False
    
    try:
        import ragas
        print("✅ RAGAS imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import RAGAS: {e}")
        return False
    
    try:
        import datasets
        print("✅ Datasets imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Datasets: {e}")
        return False
    
    return True

def test_rag_pipeline():
    """Test if RAG pipeline can be initialized"""
    try:
        from src.utils.rag_pipeline import create_rag_pipeline
        print("✅ RAG pipeline module imported successfully")
        
        # Try to create a simple RAG pipeline
        rag = create_rag_pipeline()
        print("✅ RAG pipeline created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create RAG pipeline: {e}")
        return False

if __name__ == "__main__":
    print("Testing RAG system...")
    print("=" * 40)
    
    if test_rag_imports():
        print("\n✅ All RAG dependencies imported successfully")
        print("\nTesting RAG pipeline...")
        if test_rag_pipeline():
            print("\n✅ RAG system is working!")
        else:
            print("\n❌ RAG system has issues")
    else:
        print("\n❌ RAG dependencies are missing")