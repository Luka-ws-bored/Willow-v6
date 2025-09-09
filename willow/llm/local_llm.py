import os
import requests
import json
import time

def run_local_llm(prompt: str) -> str:
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 100
        }
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 404:
                return f"Model {model} not found. Please run: ollama pull {model}"
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                return f"Ollama error: {data['error']}"
            return data.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                return f"Error calling Ollama API after {max_retries} attempts: {str(e)}"
            time.sleep(1)  # Wait before retrying
