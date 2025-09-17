"""
Tests for enhanced retry logic and circuit breaker functionality.
"""

import unittest
import asyncio
import time
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestRetryLogic(unittest.TestCase):
    """Test retry logic and circuit breaker functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up test environment."""
        self.loop.close()
    
    def test_retry_logic_import(self):
        """Test that retry logic can be imported."""
        try:
            from utils.retry_logic import (
                RAGRetryConfig, with_retry, with_async_retry,
                CircuitBreaker, AsyncCircuitBreaker
            )
            self.assertTrue(hasattr(RAGRetryConfig, 'max_retries'))
            self.assertTrue(callable(with_retry))
            self.assertTrue(callable(with_async_retry))
            print("✅ Retry logic imports successful")
        except ImportError as e:
            self.skipTest(f"Retry logic not available: {e}")
    
    def test_circuit_breaker_basic_functionality(self):
        """Test basic circuit breaker functionality."""
        try:
            from utils.retry_logic import CircuitBreaker
            
            # Create circuit breaker with low thresholds for testing
            cb = CircuitBreaker(
                failure_threshold=2,
                recovery_timeout=0.2
            )
            
            # Test normal operation
            self.assertEqual(cb.state, "CLOSED")
            
            # Test successful call
            result = cb.call(lambda: "success")
            self.assertEqual(result, "success")
            self.assertEqual(cb.failure_count, 0)
            
            # Test failure scenarios
            def failing_function():
                raise Exception("Test failure")
            
            # First failure
            with self.assertRaises(Exception):
                cb.call(failing_function)
            self.assertEqual(cb.failure_count, 1)
            self.assertEqual(cb.state, "CLOSED")
            
            # Second failure should open circuit
            with self.assertRaises(Exception):
                cb.call(failing_function)
            self.assertEqual(cb.state, "OPEN")
            
            # Third call should be rejected immediately
            with self.assertRaises(Exception) as context:
                cb.call(failing_function)
            self.assertIn("Circuit breaker is OPEN", str(context.exception))
            
            print("✅ Circuit breaker basic functionality test passed")
            
        except ImportError:
            self.skipTest("Circuit breaker not available")
    
    def test_async_circuit_breaker(self):
        """Test async circuit breaker functionality."""
        async def run_async_test():
            try:
                from utils.retry_logic import AsyncCircuitBreaker
                
                cb = AsyncCircuitBreaker(
                    failure_threshold=2,
                    recovery_timeout=0.2
                )
                
                # Test successful async call
                async def success_func():
                    return "async success"
                
                result = await cb.call(success_func())
                self.assertEqual(result, "async success")
                
                # Test failure handling
                async def failing_func():
                    raise Exception("Async test failure")
                
                # First failure
                with self.assertRaises(Exception):
                    await cb.call(failing_func())
                
                # Second failure should open circuit
                with self.assertRaises(Exception):
                    await cb.call(failing_func())
                
                self.assertEqual(cb.state, "OPEN")
                
                # Test circuit breaker rejection
                with self.assertRaises(Exception) as context:
                    await cb.call(failing_func())
                self.assertIn("Circuit breaker is OPEN", str(context.exception))
                
                print("✅ Async circuit breaker test passed")
                
            except ImportError:
                self.skipTest("Async circuit breaker not available")
        
        self.loop.run_until_complete(run_async_test())
    
    def test_retry_decorator(self):
        """Test retry decorator functionality."""
        try:
            from utils.retry_logic import with_retry
            
            # Test successful retry after failures
            attempt_count = 0
            
            @with_retry(RAGRetryConfig(max_retries=3, initial_delay=0.01))
            def sometimes_failing_function():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count < 3:
                    raise Exception(f"Attempt {attempt_count} failed")
                return f"Success on attempt {attempt_count}"
            
            result = sometimes_failing_function()
            self.assertEqual(result, "Success on attempt 3")
            self.assertEqual(attempt_count, 3)
            
            print("✅ Retry decorator test passed")
            
        except ImportError:
            self.skipTest("Retry decorator not available")
    
    def test_async_retry_decorator(self):
        """Test async retry decorator functionality."""
        async def run_async_retry_test():
            try:
                from utils.retry_logic import with_async_retry
                
                attempt_count = 0
                
                @with_async_retry(RAGRetryConfig(max_retries=3, initial_delay=0.01))
                async def sometimes_failing_async_function():
                    nonlocal attempt_count
                    attempt_count += 1
                    if attempt_count < 3:
                        raise Exception(f"Async attempt {attempt_count} failed")
                    return f"Async success on attempt {attempt_count}"
                
                result = await sometimes_failing_async_function()
                self.assertEqual(result, "Async success on attempt 3")
                self.assertEqual(attempt_count, 3)
                
                print("✅ Async retry decorator test passed")
                
            except ImportError:
                self.skipTest("Async retry decorator not available")
        
        self.loop.run_until_complete(run_async_retry_test())
    
    def test_rag_retry_integration(self):
        """Test RAG-specific retry functionality."""
        async def run_rag_retry_test():
            try:
                from utils.retry_logic import with_rag_retry, RAGOperationMetrics
                
                # Test RAG retry with metrics
                metrics = RAGOperationMetrics()
                
                @with_rag_retry(
                    config=RAGRetryConfig(max_retries=2, initial_delay=0.01),
                    operation_name="test_rag_op"
                )
                async def mock_rag_operation():
                    metrics.record_attempt()
                    # Succeed on second attempt
                    if metrics.total_attempts < 2:
                        raise Exception("RAG operation failed")
                    return "RAG success"
                
                result = await mock_rag_operation()
                self.assertEqual(result, "RAG success")
                self.assertEqual(metrics.total_attempts, 2)
                
                print("✅ RAG retry integration test passed")
                
            except ImportError:
                self.skipTest("RAG retry functionality not available")
        
        self.loop.run_until_complete(run_rag_retry_test())
    
    def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout."""
        async def run_recovery_test():
            try:
                from utils.retry_logic import AsyncCircuitBreaker
                
                cb = AsyncCircuitBreaker(
                    failure_threshold=1,
                    recovery_timeout=0.1
                )
                
                # Cause circuit to open
                async def failing_func():
                    raise Exception("Test failure")
                
                with self.assertRaises(Exception):
                    await cb.call(failing_func())
                
                self.assertEqual(cb.state, "OPEN")
                
                # Wait for recovery timeout
                await asyncio.sleep(0.12)
                
                # Circuit should now be in HALF_OPEN state
                # Next successful call should close it
                async def success_func():
                    return "recovery success"
                
                result = await cb.call(success_func())
                self.assertEqual(result, "recovery success")
                self.assertEqual(cb.state, "CLOSED")
                
                print("✅ Circuit breaker recovery test passed")
                
            except ImportError:
                self.skipTest("Async circuit breaker not available")
        
        self.loop.run_until_complete(run_recovery_test())
    
    def test_rag_retry_config(self):
        """Test RAG retry configuration."""
        try:
            from utils.retry_logic import RAGRetryConfig
            
            # Test default config
            config = RAGRetryConfig()
            self.assertEqual(config.max_retries, 3)
            self.assertEqual(config.initial_delay, 1.0)
            self.assertEqual(config.max_delay, 30.0)
            self.assertEqual(config.backoff_multiplier, 2.0)
            
            # Test custom config
            custom_config = RAGRetryConfig(
                max_retries=5,
                initial_delay=0.5,
                max_delay=30.0,
                backoff_multiplier=1.5
            )
            self.assertEqual(custom_config.max_retries, 5)
            self.assertEqual(custom_config.initial_delay, 0.5)
            
            # Test delay calculation
            delays = [custom_config.get_delay(i) for i in range(4)]
            # Note: delays have jitter, so we check approximate values
            self.assertGreater(delays[0], 0.35)  # ~0.5 with jitter
            self.assertLess(delays[0], 0.65)
            
            print("✅ RAG retry config test passed")
            
        except ImportError:
            self.skipTest("RAG retry config not available")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)