#!/usr/bin/env python3
"""
Check RAG system status
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_rag_status():
    """Check if RAG is available"""
    try:
        # Try to import RAG components
        from src.main import RAG_AVAILABLE
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        
        if RAG_AVAILABLE:
            print("✅ RAG system is available")
            
            # Try to import RAG pipeline
            try:
                from src.utils.rag_pipeline import get_rag_pipeline
                print("✅ RAG pipeline is accessible")
                return True
            except Exception as e:
                print(f"❌ RAG pipeline import failed: {e}")
                return False
        else:
            print("❌ RAG system is not available")
            return False
            
    except Exception as e:
        print(f"❌ Failed to check RAG status: {e}")
        return False

if __name__ == "__main__":
    print("Checking RAG system status...")
    print("=" * 30)
    
    result = check_rag_status()
    
    if result:
        print("\n🎉 RAG system is ready!")
    else:
        print("\n💥 RAG system needs attention")