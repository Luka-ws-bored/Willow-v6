#!/usr/bin/env python3
"""
Test Local LLM Connection
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_local_llm():
    """Test local LLM connection"""
    try:
        from willow.llm.local_llm import run_local_llm
        
        print("Testing local LLM connection...")
        response = run_local_llm("Hello, how are you?")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Local LLM test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Local LLM Connection")
    print("=" * 30)
    
    result = test_local_llm()
    
    if result:
        print("\n✅ Local LLM is working!")
    else:
        print("\n❌ Local LLM has issues")