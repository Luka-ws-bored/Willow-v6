#!/usr/bin/env python3
"""
Minimal RAG test to check if system is working
"""

def test_rag_minimal():
    """Test if we can import RAG components"""
    try:
        # Try to import the RAG availability flag
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try a direct import approach
        from src.main import RAG_AVAILABLE
        print(f"RAG_AVAILABLE = {RAG_AVAILABLE}")
        
        if RAG_AVAILABLE:
            print("✅ RAG system is available")
            return True
        else:
            print("❌ RAG system is not available")
            return False
    except Exception as e:
        print(f"Error testing RAG: {e}")
        return False

if __name__ == "__main__":
    print("Minimal RAG Test")
    print("=" * 20)
    test_rag_minimal()