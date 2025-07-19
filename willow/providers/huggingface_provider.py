"""
Hugging Face Provider for Willow v6

This module provides integration with Hugging Face inference endpoints.
"""

import os
import logging
from typing import Optional, Dict, Any
from huggingface_hub import InferenceClient


class HuggingFaceProvider:
    """
    Provider for Hugging Face inference endpoints.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "tiiuae/falcon-7b-instruct"):
        """
        Initialize the Hugging Face provider.
        
        Args:
            api_key: Hugging Face API key. If not provided, will try to get from HUGGINGFACE_API_KEY env var.
            model: Model name to use for inference
        """
        self.logger = logging.getLogger(__name__)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("HUGGINGFACE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Hugging Face API key not provided. Set HUGGINGFACE_API_KEY environment variable.")
        
        self.model = model
        
        # Initialize the inference client
        try:
            self.client = InferenceClient(token=self.api_key)
            self.logger.info(f"Hugging Face provider initialized with model: {model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Hugging Face client: {e}")
            raise
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Hugging Face inference.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        try:
            params = {
                "max_new_tokens": kwargs.get("max_tokens", 64),
                "temperature": kwargs.get("temperature", 0.7),
                "do_sample": True,
                "top_p": kwargs.get("top_p", 0.9),
            }
            # The text_generation method returns a generator, so we need to get the first result
            gen = self.client.text_generation(prompt=prompt, model=self.model, **params)
            try:
                result = next(gen)
                return result.generated_text if hasattr(result, 'generated_text') else str(result)
            except StopIteration:
                return "[HUGGINGFACE ERROR] No response generated."
        except Exception as e:
            self.logger.error(f"Error generating response with Hugging Face: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"[HUGGINGFACE ERROR] {str(e)}"
    
    def chat_completion(self, messages: list, **kwargs) -> str:
        """
        Generate a chat completion using Hugging Face.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        try:
            # Convert OpenAI-style messages to a single prompt
            prompt = self._format_messages_for_huggingface(messages)
            return self.generate_response(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in chat completion with Hugging Face: {e}")
            return f"[HUGGINGFACE ERROR] {str(e)}"
    
    def _format_messages_for_huggingface(self, messages: list) -> str:
        """
        Format OpenAI-style messages for Hugging Face models.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted prompt string
        """
        formatted = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                formatted.append(f"System: {content}")
            elif role == 'user':
                formatted.append(f"User: {content}")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}")
        
        return "\n".join(formatted)
    
    def is_available(self) -> bool:
        """
        Check if the Hugging Face provider is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model": self.model,
            "provider": "huggingface",
            "available": self.is_available()
        } 