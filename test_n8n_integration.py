#!/usr/bin/env python3
"""
Test script for n8n-Willow-Ollama integration.
This script verifies that all components are working together correctly.
"""

import requests
import json
import time
import os

def test_ollama_connection():
    """Test direct connection to Ollama."""
    print("Testing Ollama connection...")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            models = response.json()
            print(f"   Available models: {[model['name'] for model in models.get('models', [])]}")
            return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama connection: {e}")
        return False

def test_willow_backend():
    """Test Willow backend health endpoint."""
    print("\nTesting Willow backend...")
    willow_url = os.getenv("WILLOW_URL", "http://localhost:5000")
    
    try:
        response = requests.get(f"{willow_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Willow backend is running")
            print(f"   Health info: {response.json()}")
            return True
        else:
            print(f"❌ Willow backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Willow backend")
        return False
    except Exception as e:
        print(f"❌ Error testing Willow backend: {e}")
        return False

def test_willow_llm_status():
    """Test Willow's LLM status endpoint."""
    print("\nTesting Willow LLM status...")
    willow_url = os.getenv("WILLOW_URL", "http://localhost:5000")
    
    try:
        response = requests.get(f"{willow_url}/llm/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ LLM Status: {'Connected' if status.get('connected') else 'Disconnected'}")
            print(f"   Backend: {status.get('backend')}")
            print(f"   URL: {status.get('url')}")
            if 'models' in status:
                print(f"   Models: {len(status['models'])} available")
            if 'error' in status:
                print(f"   Error: {status['error']}")
            return status.get('connected', False)
        else:
            print(f"❌ LLM status endpoint returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Willow LLM status endpoint")
        return False
    except Exception as e:
        print(f"❌ Error testing LLM status: {e}")
        return False

def test_simple_chat():
    """Test a simple chat interaction."""
    print("\nTesting simple chat interaction...")
    willow_url = os.getenv("WILLOW_URL", "http://localhost:5000")
    
    try:
        response = requests.post(
            f"{willow_url}/chat",
            json={"message": "Hello, this is a test message"},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response: {result.get('response', 'No response content')}")
            return True
        else:
            print(f"❌ Chat endpoint returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to chat endpoint")
        return False
    except Exception as e:
        print(f"❌ Error testing chat endpoint: {e}")
        return False

def test_n8n_connection():
    """Test n8n connection."""
    print("\nTesting n8n connection...")
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    
    try:
        response = requests.get(f"{n8n_url}", timeout=10)
        if response.status_code == 200:
            print("✅ n8n is accessible")
            return True
        else:
            print(f"❌ n8n returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to n8n")
        return False
    except Exception as e:
        print(f"❌ Error testing n8n connection: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🚀 Starting n8n-Willow-Ollama integration tests...\n")
    
    tests = [
        test_ollama_connection,
        test_willow_backend,
        test_willow_llm_status,
        test_simple_chat,
        test_n8n_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print(f"\n🏁 Integration tests completed: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return False

if __name__ == "__main__":
    main()