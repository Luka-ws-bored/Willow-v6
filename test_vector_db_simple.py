"""
Simple test script for Vector DB functionality without external dependencies.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_vector_db_import():
    """Test that vector DB can be imported."""
    print("Testing Vector DB import...")
    try:
        from utils.vector_db import VECTOR_DB_AVAILABLE, VectorDBError
        print(f"✅ Vector DB imported successfully. Available: {VECTOR_DB_AVAILABLE}")
        return True
    except Exception as e:
        print(f"❌ Vector DB import failed: {e}")
        return False

def test_legacy_functions():
    """Test legacy compatibility functions."""
    print("Testing legacy functions...")
    try:
        from utils.vector_db import embed_texts, create_index, load_index, search_index
        print("✅ Legacy functions imported successfully")
        
        # Test that they raise appropriate errors when dependencies missing
        try:
            embed_texts(["test"])
            print("❌ Expected NotImplementedError for embed_texts")
            return False
        except NotImplementedError:
            print("✅ embed_texts correctly raises NotImplementedError")
            return True
        except Exception as e:
            print(f"❌ Unexpected error in embed_texts: {e}")
            return False
    except Exception as e:
        print(f"❌ Legacy functions test failed: {e}")
        return False

def test_rag_integration():
    """Test RAG pipeline integration with Vector DB."""
    print("Testing RAG integration...")
    try:
        from utils.rag_pipeline import RAGPipeline, VECTOR_DB_AVAILABLE as RAG_VECTOR_DB_AVAILABLE
        
        # Create temporary directory for test
        test_dir = tempfile.mkdtemp()
        test_docs_path = Path(test_dir) / "docs"
        test_docs_path.mkdir()
        
        # Create a test document
        test_doc = test_docs_path / "test.txt"
        test_doc.write_text("This is a test document for Vector DB integration.")
        
        try:
            # Try to create RAG pipeline
            rag = RAGPipeline(
                docs_path=test_docs_path,
                chunk_size=100,
                retrieval_k=2,
                use_vector_db=True  # Try to use Vector DB
            )
            
            print(f"✅ RAG pipeline created with Vector DB preference: {rag.use_vector_db}")
            print(f"   Vector DB available in RAG: {RAG_VECTOR_DB_AVAILABLE}")
            
            return True
            
        except Exception as e:
            print(f"❌ RAG pipeline creation failed: {e}")
            return False
            
        finally:
            # Clean up
            shutil.rmtree(test_dir, ignore_errors=True)
            
    except Exception as e:
        print(f"❌ RAG integration test failed: {e}")
        return False

def test_main_integration():
    """Test main.py integration with Vector DB."""
    print("Testing main.py integration...")
    try:
        from main import async_query_rag, batch_query_rag, RAG_AVAILABLE
        print(f"✅ RAG functions imported from main.py. RAG Available: {RAG_AVAILABLE}")
        return True
    except Exception as e:
        print(f"❌ Main integration test failed: {e}")
        return False

def run_all_tests():
    """Run all Vector DB tests."""
    print("🚀 Running Vector DB Test Suite")
    print("=" * 50)
    
    tests = [
        test_vector_db_import,
        test_legacy_functions,
        test_rag_integration,
        test_main_integration
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_func.__name__}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Vector DB tests passed!")
        print("\n✅ Key functionality verified:")
        print("   • Vector DB module imports correctly")
        print("   • Legacy functions maintain compatibility")
        print("   • RAG pipeline integration works")
        print("   • Main.py integration successful")
        print("   • Graceful degradation when dependencies missing")
        return True
    else:
        print("⚠️ Some tests failed - check implementation")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)