#!/usr/bin/env python3
"""
Simple RAG test
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple_imports():
    """Test simple RAG imports"""
    try:
        from src.main import RAG_AVAILABLE
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing simple RAG import...")
    result = test_simple_imports()
    if result:
        print("✅ Import successful")
    else:
        print("❌ Import failed")