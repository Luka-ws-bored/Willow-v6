import requests
import json

def test_backend():
    try:
        # Test the Flask backend
        response = requests.post('http://localhost:5000/chat', 
                                json={"message": "Hello from test!"})
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend responded: {data['response']}")
            return True
        else:
            print(f"✗ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Flask backend...")
    test_backend()