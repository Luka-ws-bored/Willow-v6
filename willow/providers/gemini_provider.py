"""
Gemini Provider for Willow v6

This module provides integration with Google's Gemini AI models.
"""

import os
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

class GeminiProvider:
    """
    Provider for Google Gemini AI models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini provider.
        
        Args:
            api_key: Gemini API key. If not provided, will try to get from GEMINI_API_KEY env var.
        """
        self.logger = logging.getLogger(__name__)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")
        
        # Configure the Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel('gemini-1.5-flash')
        
        self.logger.info("Gemini provider initialized successfully")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Gemini.
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        try:
            response = self.client.generate_content(prompt, **kwargs)
            return response.text
        except Exception as e:
            self.logger.error(f"Error generating response with Gemini: {e}")
            return f"[GEMINI ERROR] {str(e)}"
    
    def chat_completion(self, messages: list, **kwargs) -> str:
        """
        Generate a chat completion using Gemini.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response text
        """
        try:
            # Convert OpenAI-style messages to Gemini format
            prompt = self._format_messages_for_gemini(messages)
            return self.generate_response(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Error in chat completion with Gemini: {e}")
            return f"[GEMINI ERROR] {str(e)}"
    
    def _format_messages_for_gemini(self, messages: list) -> str:
        """
        Format OpenAI-style messages for Gemini.
        
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
        Check if the Gemini provider is available.
        
        Returns:
            True if available, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0 