import requests
import os

url = "http://localhost:11434/api/generate"
payload = {
    "model": "llama3.1:8b",  # Use the exact model name we know is installed
    "prompt": "Hello",
    "stream": False
}
try:
    r = requests.post(url, json=payload, timeout=30)
    print("Status code:", r.status_code)
    print("Response:", r.text)
except Exception as e:
    print("Error:", e)
