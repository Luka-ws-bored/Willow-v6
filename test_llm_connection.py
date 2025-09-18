#!/usr/bin/env python3
"""
Test LLM connection with the specific model
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_llm_connection():
    """Test connection to the specific LLM model"""
    try:
        from willow.llm.local_llm import run_local_llm
        import os
        
        # Set the model explicitly
        os.environ['OLLAMA_MODEL'] = 'goekdenizguelmez/josiefied-qwen3:1.7b'
        
        print("Testing connection to goekdenizguelmez/josiefied-qwen3:1.7b...")
        response = run_local_llm("Hello, this is a test. Please respond briefly.")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"LLM connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing LLM Connection to goekdenizguelmez/josiefied-qwen3:1.7b")
    print("=" * 60)
    
    result = test_llm_connection()
    
    if result:
        print("\n✅ LLM connection is working!")
    else:
        print("\n❌ LLM connection has issues")