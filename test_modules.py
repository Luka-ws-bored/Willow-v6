import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

def test_core_modules():
    try:
        import core.llm_adapter
        print("✓ core.llm_adapter imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core.llm_adapter: {e}")
    
    try:
        import core.embeddings
        print("✓ core.embeddings imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core.embeddings: {e}")
        
    try:
        import core.retriever
        print("✓ core.retriever imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core.retriever: {e}")
        
    try:
        import core.memory.short_memory
        print("✓ core.memory.short_memory imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core.memory.short_memory: {e}")
        
    try:
        import core.memory.long_memory
        print("✓ core.memory.long_memory imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core.memory.long_memory: {e}")

if __name__ == "__main__":
    test_core_modules()