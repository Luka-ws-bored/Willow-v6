"""
Willow v6 - AI Automation Framework

A modular AI assistant framework with dynamic plugin loading capabilities.
"""

import os

__version__ = "6.0.0"
__author__ = "Willow Team"
__description__ = "AI Automation Framework with Dynamic Plugin Loading"

# Validate required environment variables
def validate_environment():
    """Validate that required environment variables are set."""
    required_keys = []
    optional_keys = ["OPENROUTER_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "HUGGINGFACE_API_KEY"]
    
    missing_required = [key for key in required_keys if not os.environ.get(key)]
    if missing_required:
        raise ValueError(f"Missing required environment variables: {missing_required}")
    
    available_keys = [key for key in optional_keys if os.environ.get(key)]
    if not available_keys:
        print("Warning: No API keys found. Set OPENROUTER_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, or HUGGINGFACE_API_KEY for full functionality.")
    else:
        print(f"Available API providers: {available_keys}")

from .plugin_loader import load_plugins, get_plugin_info, validate_plugin

__all__ = ['load_plugins', 'get_plugin_info', 'validate_plugin', 'validate_environment'] 