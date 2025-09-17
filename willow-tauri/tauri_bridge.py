#!/usr/bin/env python3
"""
Willow Tauri Bridge Script
A bridge between the Tauri desktop app and Willow v6 Python backend.
Handles CLI-style commands from the Rust frontend.
"""

import sys
import json
import argparse
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to Python path to import Willow modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

try:
    from src.main import (
        query_llm, 
        async_query_llm, 
        async_query_rag_simple,
        list_available_models,
        get_performance_stats,
        RAG_AVAILABLE,
        get_version_info,
        CAPABILITIES
    )
    WILLOW_AVAILABLE = True
except ImportError as e:
    print(f"Error importing Willow modules: {e}", file=sys.stderr)
    WILLOW_AVAILABLE = False

def create_response(success: bool, data: Optional[Any] = None, error: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized response format."""
    return {
        "success": success,
        "data": data,
        "error": error,
        "timestamp": asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else None
    }

def handle_llm_query(prompt: str, model: Optional[str] = None, max_tokens: Optional[int] = None) -> Dict[str, Any]:
    """Handle LLM query requests."""
    if not WILLOW_AVAILABLE:
        return create_response(False, error="Willow backend not available")
    
    try:
        # Use async version for better performance
        async def query_async():
            return await async_query_llm(
                prompt=prompt,
                model_preference=model,
                max_tokens=max_tokens
            )
        
        # Run async query
        response = asyncio.run(query_async())
        return create_response(True, data=response)
        
    except Exception as e:
        return create_response(False, error=f"LLM query failed: {str(e)}")

def handle_rag_query(query: str, documents: Optional[list] = None, top_k: Optional[int] = None) -> Dict[str, Any]:
    """Handle RAG query requests."""
    if not WILLOW_AVAILABLE:
        return create_response(False, error="Willow backend not available")
    
    if not RAG_AVAILABLE:
        return create_response(False, error="RAG functionality not available - missing dependencies")
    
    try:
        async def rag_query_async():
            if documents:
                # Use provided documents
                return await async_query_rag_simple(
                    query=query,
                    documents=documents,
                    top_k=top_k or 3
                )
            else:
                # Use default RAG pipeline from config
                from src.utils.rag_pipeline import get_rag_pipeline
                rag_pipeline = get_rag_pipeline()
                result = rag_pipeline.query_with_context(query, top_k=top_k or 3)
                return result.get('response', 'No response generated')
        
        response = asyncio.run(rag_query_async())
        return create_response(True, data=response)
        
    except Exception as e:
        return create_response(False, error=f"RAG query failed: {str(e)}")

def handle_status_query() -> Dict[str, Any]:
    """Handle status and capability queries."""
    if not WILLOW_AVAILABLE:
        return create_response(False, error="Willow backend not available")
    
    try:
        version_info = get_version_info()
        status_data = {
            "version": version_info.get("version", "unknown"),
            "capabilities": CAPABILITIES,
            "rag_available": RAG_AVAILABLE,
            "models": list_available_models(),
            "performance_stats": get_performance_stats()
        }
        
        return create_response(True, data=status_data)
        
    except Exception as e:
        return create_response(False, error=f"Status query failed: {str(e)}")

def main():
    """Main entry point for the bridge script."""
    parser = argparse.ArgumentParser(description="Willow Tauri Bridge")
    parser.add_argument("--mode", required=True, choices=["llm", "rag", "status"], 
                       help="Operation mode")
    
    # LLM specific arguments
    parser.add_argument("--prompt", help="Prompt for LLM query")
    parser.add_argument("--model", help="Preferred model name")
    parser.add_argument("--max-tokens", type=int, help="Maximum tokens in response")
    
    # RAG specific arguments
    parser.add_argument("--query", help="Query for RAG search")
    parser.add_argument("--documents", nargs="*", help="Documents to search (optional)")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top results")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        if args.mode == "llm":
            if not args.prompt:
                result = create_response(False, error="Prompt is required for LLM mode")
            else:
                result = handle_llm_query(args.prompt, args.model, args.max_tokens)
        
        elif args.mode == "rag":
            if not args.query:
                result = create_response(False, error="Query is required for RAG mode")
            else:
                result = handle_rag_query(args.query, args.documents, args.top_k)
        
        elif args.mode == "status":
            result = handle_status_query()
        
        else:
            result = create_response(False, error=f"Unknown mode: {args.mode}")
    
    except Exception as e:
        result = create_response(False, error=f"Unexpected error: {str(e)}")
    
    # Output result as JSON
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()