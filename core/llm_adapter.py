"""
Ollama LLM Adapter for Willow Framework
"""
import os
import requests
from typing import Dict, Any, Optional


class OllamaAdapter:
    """Adapter for interacting with Ollama LLM service."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Ollama adapter.
        
        Args:
            base_url: Base URL for the Ollama service. 
                     Defaults to OLLAMA_URL environment variable or http://localhost:11434
        """
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.health_endpoint = f"{self.base_url}/api/health"
        self.generate_endpoint = f"{self.base_url}/api/generate"
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the Ollama service.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            response = requests.get(self.health_endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def generate(self, model: str, prompt: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate text using Ollama.
        
        Args:
            model: The model to use for generation
            prompt: The prompt to send to the model
            options: Additional options for the generation
            
        Returns:
            Dictionary containing the generation response
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        if options:
            payload["options"] = options
            
        try:
            response = requests.post(self.generate_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def chat(self, model: str = "llama2", messages: list = None) -> Dict[str, Any]:
        """
        Chat with Ollama using the chat endpoint.
        
        Args:
            model: The model to use for chat (default: llama2)
            messages: List of message dictionaries with role and content
            
        Returns:
            Dictionary containing the chat response
        """
        if messages is None:
            messages = []
            
        chat_endpoint = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(chat_endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Example usage:
# adapter = OllamaAdapter()
# health = adapter.health_check()
# response = adapter.generate("llama2", "Hello, how are you?")