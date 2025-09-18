import requests
import time

def test_backend():
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test LLM status endpoint
    try:
        response = requests.get("http://localhost:5000/llm/status", timeout=5)
        print(f"LLM status: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"LLM status check failed: {e}")

if __name__ == "__main__":
    test_backend()