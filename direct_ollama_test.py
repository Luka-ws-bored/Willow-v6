#!/usr/bin/env python3
"""
Direct Ollama test
"""

import requests
import json

def test_ollama_direct():
    """Test Ollama directly with requests"""
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "goekdenizguelmez/josiefied-qwen3:1.7b",
            "prompt": "Hello, how are you?",
            "stream": False
        }
        
        print("Testing Ollama directly...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response field')}")
            return True
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Direct Ollama test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Direct Ollama Connection")
    print("=" * 35)
    
    result = test_ollama_direct()
    
    if result:
        print("\n✅ Direct Ollama connection is working!")
    else:
        print("\n❌ Direct Ollama connection has issues")