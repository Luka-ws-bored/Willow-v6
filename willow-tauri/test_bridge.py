#!/usr/bin/env python3
"""
Test script for Willow Tauri Bridge
Tests all functionality to ensure proper integration
"""

import subprocess
import sys
import json
from pathlib import Path

def run_bridge_test(mode, **kwargs):
    """Run a test command on the bridge script."""
    cmd = ["python", "tauri_bridge.py", "--mode", mode]
    
    # Add arguments based on mode
    if mode == "llm" and "prompt" in kwargs:
        cmd.extend(["--prompt", kwargs["prompt"]])
        if "model" in kwargs:
            cmd.extend(["--model", kwargs["model"]])
        if "max_tokens" in kwargs:
            cmd.extend(["--max-tokens", str(kwargs["max_tokens"])])
    
    elif mode == "rag" and "query" in kwargs:
        cmd.extend(["--query", kwargs["query"]])
        if "top_k" in kwargs:
            cmd.extend(["--top-k", str(kwargs["top_k"])])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                return True, response
            except json.JSONDecodeError:
                return False, f"Invalid JSON response: {result.stdout}"
        else:
            return False, f"Process failed: {result.stderr}"
    
    except subprocess.TimeoutExpired:
        return False, "Test timed out (30s)"
    except Exception as e:
        return False, f"Test error: {str(e)}"

def main():
    print("🧪 Testing Willow Tauri Bridge")
    print("=" * 40)
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    original_dir = Path.cwd()
    
    try:
        import os
        os.chdir(script_dir)
        
        # Test 1: Status check
        print("\n📊 Testing status query...")
        success, response = run_bridge_test("status")
        if success:
            print("✅ Status test passed")
            if response.get("success"):
                data = response.get("data", {})
                print(f"   Version: {data.get('version', 'Unknown')}")
                print(f"   RAG Available: {data.get('rag_available', False)}")
                capabilities = data.get('capabilities', {})
                print(f"   Capabilities: {sum(capabilities.values())}/{len(capabilities)} available")
            else:
                print(f"⚠️  Backend error: {response.get('error', 'Unknown error')}")
        else:
            print(f"❌ Status test failed: {response}")
        
        # Test 2: LLM query
        print("\n💬 Testing LLM query...")
        success, response = run_bridge_test("llm", prompt="Hello, this is a test message. Please respond briefly.")
        if success:
            print("✅ LLM test passed")
            if response.get("success"):
                print(f"   Response: {response.get('data', 'No data')[:100]}...")
            else:
                print(f"⚠️  LLM error: {response.get('error', 'Unknown error')}")
        else:
            print(f"❌ LLM test failed: {response}")
        
        # Test 3: RAG query (if available)
        print("\n📚 Testing RAG query...")
        success, response = run_bridge_test("rag", query="What is artificial intelligence?", top_k=3)
        if success:
            print("✅ RAG test passed")
            if response.get("success"):
                print(f"   Response: {response.get('data', 'No data')[:100]}...")
            else:
                print(f"⚠️  RAG error: {response.get('error', 'Unknown error')}")
        else:
            print(f"❌ RAG test failed: {response}")
        
        # Test 4: Invalid mode
        print("\n🚫 Testing error handling...")
        success, response = run_bridge_test("invalid_mode")
        if not success or not response.get("success"):
            print("✅ Error handling works correctly")
        else:
            print("⚠️  Error handling may need improvement")
        
        print("\n" + "=" * 40)
        print("🏁 Bridge testing complete!")
        print("\nIf all tests passed, you can proceed with:")
        print("  npm run tauri:dev    # Development mode")
        print("  npm run tauri:build  # Production build")
        
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    main()