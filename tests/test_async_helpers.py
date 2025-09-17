"""
Tests for async batch processing helpers and document operations.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestAsyncHelpers(unittest.TestCase):
    """Test async helper functions and batch processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.loop.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_async_helpers_import(self):
        """Test that async helpers can be imported."""
        try:
            from utils.async_helpers import (
                async_batch_operation, async_file_read, async_file_write,
                DocumentBatchProcessor, async_rag_document_ingestion,
                async_batch_file_processing, get_async_stats
            )
            self.assertTrue(callable(async_batch_operation))
            self.assertTrue(callable(async_file_read))
            self.assertTrue(callable(async_file_write))
            self.assertTrue(callable(DocumentBatchProcessor))
            print("✅ Async helpers imports successful")
        except ImportError as e:
            self.skipTest(f"Async helpers not available: {e}")
    
    def test_async_file_operations(self):
        """Test async file read/write operations."""
        async def run_file_test():
            try:
                from utils.async_helpers import async_file_read, async_file_write
                
                # Test file write
                test_file = self.temp_path / "test_async.txt"
                test_content = "Test async file operations"
                
                await async_file_write(str(test_file), test_content)
                self.assertTrue(test_file.exists())
                
                # Test file read
                read_content = await async_file_read(str(test_file))
                self.assertEqual(read_content, test_content)
                
                print("✅ Async file operations test passed")
                
            except ImportError:
                self.skipTest("Async file operations not available")
        
        self.loop.run_until_complete(run_file_test())
    
    def test_async_batch_operation(self):
        """Test async batch operation processing."""
        async def run_batch_test():
            try:
                from utils.async_helpers import async_batch_operation
                
                # Create test operations
                def create_operation(value):
                    def operation():
                        return value * 2
                    return operation
                
                operations = [create_operation(i) for i in range(5)]
                
                # Run batch operation
                results = await async_batch_operation(operations, max_concurrent=2)
                
                expected = [i * 2 for i in range(5)]
                self.assertEqual(results, expected)
                
                print("✅ Async batch operation test passed")
                
            except ImportError:
                self.skipTest("Async batch operation not available")
        
        self.loop.run_until_complete(run_batch_test())
    
    def test_document_batch_processor(self):
        """Test DocumentBatchProcessor functionality."""
        async def run_processor_test():
            try:
                from utils.async_helpers import DocumentBatchProcessor
                
                processor = DocumentBatchProcessor(max_concurrent=2, chunk_size=3)
                
                # Test document chunk processing
                test_docs = [f"Document {i} content" for i in range(5)]
                
                async def simple_processor(doc: str) -> str:
                    return f"Processed: {doc}"
                
                results = await processor.process_document_chunks(
                    documents=test_docs,
                    processor_func=simple_processor
                )
                
                self.assertEqual(len(results), 5)
                
                # Check results format (index, result, error)
                for i, (index, result, error) in enumerate(results):
                    self.assertEqual(index, i)
                    self.assertIsNone(error)
                    self.assertIn("Processed:", result)
                
                # Check stats
                stats = processor.get_stats()
                self.assertEqual(stats['documents_processed'], 5)
                self.assertEqual(stats['batches_completed'], 1)
                self.assertEqual(stats['errors'], 0)
                
                print("✅ Document batch processor test passed")
                
            except ImportError:
                self.skipTest("Document batch processor not available")
        
        self.loop.run_until_complete(run_processor_test())
    
    def test_batch_file_processing(self):
        """Test batch file processing functionality."""
        async def run_file_batch_test():
            try:
                from utils.async_helpers import async_batch_file_processing
                
                # Create test files
                test_files = []
                for i in range(3):
                    test_file = self.temp_path / f"test_{i}.txt"
                    test_file.write_text(f"Content of file {i}")
                    test_files.append(test_file)
                
                # Process files
                async def file_processor(file_path: str, content: str) -> Dict[str, Any]:
                    return {
                        'file': Path(file_path).name,
                        'length': len(content),
                        'processed': True
                    }
                
                results = await async_batch_file_processing(
                    file_paths=test_files,
                    output_processor=file_processor,
                    max_concurrent=2
                )
                
                self.assertEqual(len(results), 3)
                
                # Check results
                for file_path, result, error in results:
                    self.assertIsNone(error)
                    self.assertIsInstance(result, dict)
                    self.assertTrue(result.get('processed', False))
                
                print("✅ Batch file processing test passed")
                
            except ImportError:
                self.skipTest("Batch file processing not available")
        
        self.loop.run_until_complete(run_file_batch_test())
    
    def test_document_processor_with_metadata(self):
        """Test document processing with metadata."""
        async def run_metadata_test():
            try:
                from utils.async_helpers import DocumentBatchProcessor
                
                processor = DocumentBatchProcessor(max_concurrent=2)
                
                # Test with metadata
                test_docs = ["Doc 1", "Doc 2", "Doc 3"]
                test_metadata = [
                    {"id": 1, "category": "A"},
                    {"id": 2, "category": "B"},
                    {"id": 3, "category": "A"}
                ]
                
                async def metadata_processor(doc: str, metadata: Dict = None) -> Dict:
                    return {
                        'document': doc,
                        'metadata': metadata,
                        'processed_at': 'test_time'
                    }
                
                results = await processor.process_document_chunks(
                    documents=test_docs,
                    processor_func=metadata_processor,
                    metadata=test_metadata
                )
                
                self.assertEqual(len(results), 3)
                
                for i, (index, result, error) in enumerate(results):
                    self.assertEqual(index, i)
                    self.assertIsNone(error)
                    self.assertEqual(result['document'], test_docs[i])
                    self.assertEqual(result['metadata'], test_metadata[i])
                
                print("✅ Document processor with metadata test passed")
                
            except ImportError:
                self.skipTest("Document processor not available")
        
        self.loop.run_until_complete(run_metadata_test())
    
    def test_error_handling_in_batch_processing(self):
        """Test error handling in batch operations."""
        async def run_error_test():
            try:
                from utils.async_helpers import DocumentBatchProcessor
                
                processor = DocumentBatchProcessor(max_concurrent=2)
                
                test_docs = ["Good doc", "Bad doc", "Another good doc"]
                
                async def error_prone_processor(doc: str) -> str:
                    if "Bad" in doc:
                        raise ValueError("Simulated processing error")
                    return f"Processed: {doc}"
                
                results = await processor.process_document_chunks(
                    documents=test_docs,
                    processor_func=error_prone_processor
                )
                
                self.assertEqual(len(results), 3)
                
                # Check first result (success)
                index, result, error = results[0]
                self.assertEqual(index, 0)
                self.assertIsNone(error)
                self.assertEqual(result, "Processed: Good doc")
                
                # Check second result (error)
                index, result, error = results[1]
                self.assertEqual(index, 1)
                self.assertIsNone(result)
                self.assertIsInstance(error, ValueError)
                
                # Check third result (success)
                index, result, error = results[2]
                self.assertEqual(index, 2)
                self.assertIsNone(error)
                self.assertEqual(result, "Processed: Another good doc")
                
                # Check error tracking in stats
                stats = processor.get_stats()
                self.assertEqual(stats['errors'], 1)
                self.assertEqual(stats['documents_processed'], 2)
                
                print("✅ Error handling test passed")
                
            except ImportError:
                self.skipTest("Document processor not available")
        
        self.loop.run_until_complete(run_error_test())
    
    def test_path_validation(self):
        """Test file path validation for security."""
        async def run_path_validation_test():
            try:
                from utils.async_helpers import DocumentBatchProcessor
                
                processor = DocumentBatchProcessor()
                
                # Create valid test files in temp directory
                valid_file = self.temp_path / "valid.txt"
                valid_file.write_text("Valid content")
                
                # Test with valid paths
                valid_paths = [valid_file]
                validated = await processor._validate_file_paths(valid_paths)
                self.assertEqual(len(validated), 1)
                
                # Test with invalid paths (should be filtered out)
                invalid_paths = [
                    "/etc/passwd",  # System file
                    "../../../etc/passwd",  # Path traversal
                    "/nonexistent/file.txt"  # Nonexistent
                ]
                validated_invalid = await processor._validate_file_paths(invalid_paths)
                self.assertEqual(len(validated_invalid), 0)
                
                print("✅ Path validation test passed")
                
            except ImportError:
                self.skipTest("Path validation not available")
        
        self.loop.run_until_complete(run_path_validation_test())
    
    def test_async_stats_tracking(self):
        """Test async statistics tracking."""
        try:
            from utils.async_helpers import get_async_stats, async_timed
            
            # Get initial stats
            initial_stats = get_async_stats()
            initial_calls = initial_stats.get('async_calls', 0)
            
            # Run a timed async operation
            @async_timed
            async def timed_operation():
                await asyncio.sleep(0.01)
                return "completed"
            
            async def run_stats_test():
                result = await timed_operation()
                self.assertEqual(result, "completed")
                
                # Check updated stats
                updated_stats = get_async_stats()
                self.assertGreater(updated_stats['async_calls'], initial_calls)
                self.assertGreater(updated_stats['total_async_time'], 0)
                
                print("✅ Async stats tracking test passed")
            
            self.loop.run_until_complete(run_stats_test())
            
        except ImportError:
            self.skipTest("Async stats not available")
    
    def test_graceful_degradation(self):
        """Test graceful degradation when optional dependencies are missing."""
        async def run_degradation_test():
            try:
                from utils.async_helpers import async_document_similarity_batch
                
                # This should fail gracefully if sentence-transformers is not available
                try:
                    query_docs = ["Test document 1", "Test document 2"]
                    reference_docs = ["Reference doc 1", "Reference doc 2"]
                    
                    results = await async_document_similarity_batch(
                        query_docs=query_docs,
                        reference_docs=reference_docs,
                        max_concurrent=1
                    )
                    
                    # If dependencies are available, should get results
                    self.assertIsInstance(results, list)
                    print("✅ Similarity processing available and working")
                    
                except ValueError as e:
                    # Expected if dependencies are missing
                    self.assertIn("similarity processing requires", str(e).lower())
                    print("✅ Graceful degradation for missing dependencies working")
                
            except ImportError:
                self.skipTest("Similarity batch processing not available")
        
        self.loop.run_until_complete(run_degradation_test())


class TestAsyncContextManager(unittest.TestCase):
    """Test async context manager functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up test environment."""
        self.loop.close()
    
    def test_async_context_manager(self):
        """Test AsyncContext manager functionality."""
        async def run_context_test():
            try:
                from utils.async_helpers import AsyncContext
                
                async with AsyncContext() as ctx:
                    # Add some tasks
                    async def test_task(value):
                        await asyncio.sleep(0.01)
                        return value * 2
                    
                    task1 = ctx.add_task(test_task(5))
                    task2 = ctx.add_task(test_task(10))
                    
                    result1 = await task1
                    result2 = await task2
                    
                    self.assertEqual(result1, 10)
                    self.assertEqual(result2, 20)
                
                print("✅ Async context manager test passed")
                
            except ImportError:
                self.skipTest("AsyncContext not available")
        
        self.loop.run_until_complete(run_context_test())


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)