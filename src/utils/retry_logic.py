"""
Retry and backoff logic for RAG operations in Willow v6.
Provides robust error handling with exponential backoff for transient failures.
"""

import asyncio
import logging
import time
import random
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, Union
from pathlib import Path
import json

# Load RAG configuration if available
def load_rag_config() -> Dict[str, Any]:
    """Load RAG configuration from config file."""
    config_path = Path(__file__).parent / "config_rag.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load RAG config: {e}")
    
    # Default configuration
    return {
        "rag_configuration": {
            "retry_logic": {
                "enable_retries": True,
                "max_retries": 3,
                "initial_delay_seconds": 1.0,
                "backoff_multiplier": 2.0,
                "max_delay_seconds": 30.0,
                "retry_on_errors": [
                    "ConnectionError",
                    "TimeoutError",
                    "TemporaryUnavailable",
                    "ServiceUnavailable"
                ]
            }
        }
    }

# Global configuration
_rag_config = load_rag_config()
_retry_config = _rag_config["rag_configuration"]["retry_logic"]

# Logger for retry operations
retry_logger = logging.getLogger('willow.rag.retry')


class RetryableError(Exception):
    """Base class for errors that should trigger retries."""
    pass


class TemporaryUnavailableError(RetryableError):
    """Service temporarily unavailable."""
    pass


class ServiceUnavailableError(RetryableError):
    """Service unavailable for an extended period."""
    pass


class RAGRetryConfig:
    """Configuration for RAG retry logic."""
    
    def __init__(
        self,
        max_retries: int = None,
        initial_delay: float = None,
        backoff_multiplier: float = None,
        max_delay: float = None,
        retry_on_errors: List[str] = None,
        jitter: bool = True
    ):
        """Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            backoff_multiplier: Exponential backoff multiplier
            max_delay: Maximum delay in seconds
            retry_on_errors: List of error types to retry on
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries or _retry_config.get("max_retries", 3)
        self.initial_delay = initial_delay or _retry_config.get("initial_delay_seconds", 1.0)
        self.backoff_multiplier = backoff_multiplier or _retry_config.get("backoff_multiplier", 2.0)
        self.max_delay = max_delay or _retry_config.get("max_delay_seconds", 30.0)
        self.retry_on_errors = retry_on_errors or _retry_config.get("retry_on_errors", [
            "ConnectionError", "TimeoutError", "TemporaryUnavailable"
        ])
        self.jitter = jitter
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if an error should trigger a retry.
        
        Args:
            error: The exception that occurred
            attempt: Current attempt number (0-based)
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False
        
        error_name = type(error).__name__
        return error_name in self.retry_on_errors or isinstance(error, RetryableError)
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.backoff_multiplier ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add ±25% jitter
            jitter_factor = 0.25
            jitter = delay * jitter_factor * (2 * random.random() - 1)
            delay += jitter
            delay = max(0, delay)
        
        return delay


def with_retry(
    config: Optional[RAGRetryConfig] = None,
    operation_name: str = "operation"
) -> Callable:
    """Decorator to add retry logic to synchronous functions.
    
    Args:
        config: Retry configuration (uses default if None)
        operation_name: Name for logging purposes
        
    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RAGRetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    start_time = time.perf_counter()
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        duration = time.perf_counter() - start_time
                        retry_logger.info(
                            f"{operation_name} succeeded on attempt {attempt + 1} "
                            f"after {duration:.3f}s"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not config.should_retry(e, attempt):
                        retry_logger.error(
                            f"{operation_name} failed permanently after {attempt + 1} attempts: {e}"
                        )
                        raise
                    
                    if attempt < config.max_retries:
                        delay = config.get_delay(attempt)
                        retry_logger.warning(
                            f"{operation_name} failed on attempt {attempt + 1}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
            
            # All retries exhausted
            retry_logger.error(
                f"{operation_name} failed after {config.max_retries + 1} attempts: {last_exception}"
            )
            raise last_exception
        
        return wrapper
    return decorator


def with_async_retry(
    config: Optional[RAGRetryConfig] = None,
    operation_name: str = "async_operation"
) -> Callable:
    """Decorator to add retry logic to async functions.
    
    Args:
        config: Retry configuration (uses default if None)
        operation_name: Name for logging purposes
        
    Returns:
        Decorated async function with retry logic
    """
    if config is None:
        config = RAGRetryConfig()
    
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    start_time = time.perf_counter()
                    result = await func(*args, **kwargs)
                    
                    if attempt > 0:
                        duration = time.perf_counter() - start_time
                        retry_logger.info(
                            f"{operation_name} succeeded on attempt {attempt + 1} "
                            f"after {duration:.3f}s"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if not config.should_retry(e, attempt):
                        retry_logger.error(
                            f"{operation_name} failed permanently after {attempt + 1} attempts: {e}"
                        )
                        raise
                    
                    if attempt < config.max_retries:
                        delay = config.get_delay(attempt)
                        retry_logger.warning(
                            f"{operation_name} failed on attempt {attempt + 1}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        await asyncio.sleep(delay)
            
            # All retries exhausted
            retry_logger.error(
                f"{operation_name} failed after {config.max_retries + 1} attempts: {last_exception}"
            )
            raise last_exception
        
        return wrapper
    return decorator


class AsyncCircuitBreaker:
    """Async-aware circuit breaker pattern for RAG operations."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
        half_open_max_calls: int = 3
    ):
        """Initialize async circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
            half_open_max_calls: Max calls allowed in HALF_OPEN state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0
        self._lock = asyncio.Lock()
    
    async def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        return (
            self.state == "OPEN" and
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    async def call(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        async with self._lock:
            if self.state == "OPEN":
                if await self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                    self.half_open_calls = 0
                    retry_logger.info("Async circuit breaker attempting recovery (HALF_OPEN)")
                else:
                    remaining_time = self.recovery_timeout - (time.time() - self.last_failure_time)
                    raise ServiceUnavailableError(
                        f"Async circuit breaker is OPEN. "
                        f"Will retry after {remaining_time:.1f}s"
                    )
            
            elif self.state == "HALF_OPEN":
                if self.half_open_calls >= self.half_open_max_calls:
                    raise ServiceUnavailableError(
                        "Async circuit breaker in HALF_OPEN state - max calls exceeded"
                    )
                self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - update circuit breaker state
            async with self._lock:
                if self.state == "HALF_OPEN":
                    self.success_count += 1
                    if self.success_count >= 2:  # Require multiple successes
                        self.state = "CLOSED"
                        self.failure_count = 0
                        self.success_count = 0
                        retry_logger.info("Async circuit breaker recovered (CLOSED)")
                elif self.state == "CLOSED":
                    # Reset failure count on successful call
                    self.failure_count = max(0, self.failure_count - 1)
            
            return result
            
        except self.expected_exception as e:
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    self.success_count = 0
                    retry_logger.warning(
                        f"Async circuit breaker opened after {self.failure_count} failures"
                    )
                elif self.state == "HALF_OPEN":
                    self.state = "OPEN"
                    self.success_count = 0
                    retry_logger.warning("Async circuit breaker re-opened during recovery attempt")
            
            raise


class CircuitBreaker:
    """Synchronous circuit breaker pattern for backward compatibility."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type that triggers circuit breaker
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        return (
            self.state == "OPEN" and
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                retry_logger.info("Circuit breaker attempting recovery (HALF_OPEN)")
            else:
                raise ServiceUnavailableError(
                    f"Circuit breaker is OPEN. "
                    f"Will retry after {self.recovery_timeout - (time.time() - self.last_failure_time):.1f}s"
                )
        
        try:
            result = func(*args, **kwargs)
            
            # Success - reset circuit breaker
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                retry_logger.info("Circuit breaker recovered (CLOSED)")
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                retry_logger.warning(
                    f"Circuit breaker opened after {self.failure_count} failures"
                )
            elif self.state == "HALF_OPEN":
                self.state = "OPEN"
                retry_logger.warning("Circuit breaker re-opened during recovery attempt")
            
            raise


# Specialized retry decorators for RAG operations
def with_rag_retry(
    config: Optional[RAGRetryConfig] = None,
    circuit_breaker: Optional[AsyncCircuitBreaker] = None,
    operation_name: str = "rag_operation"
) -> Callable:
    """Decorator specifically designed for RAG async operations.
    
    Combines retry logic with circuit breaker pattern for robust RAG operations.
    
    Args:
        config: Retry configuration (uses RAG-optimized defaults if None)
        circuit_breaker: Circuit breaker instance (creates default if None)
        operation_name: Name for logging and metrics
        
    Returns:
        Decorated async function with retry and circuit breaker logic
    """
    if config is None:
        config = RAGRetryConfig(
            max_retries=3,
            initial_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=30.0,
            retry_on_errors=[
                "ConnectionError", "TimeoutError", "TemporaryUnavailable",
                "ServiceUnavailable", "RAGError", "VectorDBError"
            ]
        )
    
    if circuit_breaker is None:
        circuit_breaker = AsyncCircuitBreaker(
            failure_threshold=3,
            recovery_timeout=30.0,
            expected_exception=Exception
        )
    
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Use circuit breaker to wrap the retry logic
            async def retry_wrapper():
                last_exception = None
                
                for attempt in range(config.max_retries + 1):
                    try:
                        start_time = time.perf_counter()
                        result = await func(*args, **kwargs)
                        
                        duration = time.perf_counter() - start_time
                        if attempt > 0:
                            retry_logger.info(
                                f"{operation_name} succeeded on attempt {attempt + 1} "
                                f"after {duration:.3f}s",
                                extra={
                                    'operation': operation_name,
                                    'attempt': attempt + 1,
                                    'duration': duration,
                                    'success': True
                                }
                            )
                        
                        return result
                        
                    except Exception as e:
                        last_exception = e
                        
                        if not config.should_retry(e, attempt):
                            retry_logger.error(
                                f"{operation_name} failed permanently after {attempt + 1} attempts: {e}",
                                extra={
                                    'operation': operation_name,
                                    'attempt': attempt + 1,
                                    'error': str(e),
                                    'permanent_failure': True
                                }
                            )
                            raise
                        
                        if attempt < config.max_retries:
                            delay = config.get_delay(attempt)
                            retry_logger.warning(
                                f"{operation_name} failed on attempt {attempt + 1}: {e}. "
                                f"Retrying in {delay:.2f}s...",
                                extra={
                                    'operation': operation_name,
                                    'attempt': attempt + 1,
                                    'error': str(e),
                                    'retry_delay': delay
                                }
                            )
                            await asyncio.sleep(delay)
                
                # All retries exhausted
                retry_logger.error(
                    f"{operation_name} failed after {config.max_retries + 1} attempts: {last_exception}",
                    extra={
                        'operation': operation_name,
                        'total_attempts': config.max_retries + 1,
                        'final_error': str(last_exception),
                        'retries_exhausted': True
                    }
                )
                raise last_exception
            
            # Execute with circuit breaker protection
            return await circuit_breaker.call(retry_wrapper)
        
        return wrapper
    return decorator


class RAGOperationMetrics:
    """Metrics collection for RAG operations with retry/circuit breaker stats."""
    
    def __init__(self):
        self.metrics = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'retries_attempted': 0,
            'circuit_breaker_trips': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'operation_types': {},
            'error_types': {}
        }
        self._lock = asyncio.Lock()
    
    async def record_operation(
        self,
        operation_name: str,
        duration: float,
        success: bool,
        attempts: int = 1,
        error_type: str = None,
        circuit_breaker_tripped: bool = False
    ):
        """Record metrics for a RAG operation."""
        async with self._lock:
            self.metrics['total_operations'] += 1
            self.metrics['total_execution_time'] += duration
            
            if success:
                self.metrics['successful_operations'] += 1
            else:
                self.metrics['failed_operations'] += 1
                if error_type:
                    self.metrics['error_types'][error_type] = \
                        self.metrics['error_types'].get(error_type, 0) + 1
            
            if attempts > 1:
                self.metrics['retries_attempted'] += (attempts - 1)
            
            if circuit_breaker_tripped:
                self.metrics['circuit_breaker_trips'] += 1
            
            # Track operation types
            self.metrics['operation_types'][operation_name] = \
                self.metrics['operation_types'].get(operation_name, 0) + 1
            
            # Update average
            if self.metrics['total_operations'] > 0:
                self.metrics['average_execution_time'] = \
                    self.metrics['total_execution_time'] / self.metrics['total_operations']
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        async with self._lock:
            return self.metrics.copy()
    
    async def reset_metrics(self):
        """Reset all metrics."""
        async with self._lock:
            self.metrics = {
                'total_operations': 0,
                'successful_operations': 0,
                'failed_operations': 0,
                'retries_attempted': 0,
                'circuit_breaker_trips': 0,
                'total_execution_time': 0.0,
                'average_execution_time': 0.0,
                'operation_types': {},
                'error_types': {}
            }


# Global metrics instance
_rag_metrics = RAGOperationMetrics()

def get_rag_metrics() -> RAGOperationMetrics:
    """Get the global RAG metrics instance."""
    return _rag_metrics
# Convenience functions for common RAG operations
def create_rag_retry_config(
    quick: bool = False,
    aggressive: bool = False,
    rag_optimized: bool = True
) -> RAGRetryConfig:
    """Create predefined retry configurations.
    
    Args:
        quick: Use quick retry settings (fewer retries, shorter delays)
        aggressive: Use aggressive retry settings (more retries, longer delays)
        rag_optimized: Use RAG-optimized settings (default)
        
    Returns:
        Configured RAGRetryConfig instance
    """
    if quick:
        return RAGRetryConfig(
            max_retries=2,
            initial_delay=0.5,
            backoff_multiplier=1.5,
            max_delay=5.0,
            retry_on_errors=["ConnectionError", "TimeoutError"]
        )
    elif aggressive:
        return RAGRetryConfig(
            max_retries=5,
            initial_delay=2.0,
            backoff_multiplier=2.5,
            max_delay=60.0,
            retry_on_errors=[
                "ConnectionError", "TimeoutError", "TemporaryUnavailable",
                "ServiceUnavailable", "RAGError", "VectorDBError"
            ]
        )
    elif rag_optimized:
        return RAGRetryConfig(
            max_retries=3,
            initial_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=30.0,
            retry_on_errors=[
                "ConnectionError", "TimeoutError", "TemporaryUnavailable",
                "RAGError", "VectorDBError"
            ],
            jitter=True
        )
    else:
        return RAGRetryConfig()


# Example usage for RAG operations
if __name__ == "__main__":
    # Test retry logic
    logging.basicConfig(level=logging.INFO)
    
    @with_retry(create_rag_retry_config(quick=True), "test_operation")
    def flaky_function():
        """Simulate a flaky function that fails sometimes."""
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise ConnectionError("Simulated connection failure")
        return "Success!"
    
    @with_async_retry(create_rag_retry_config(), "async_test_operation")
    async def async_flaky_function():
        """Async version of flaky function."""
        import random
        await asyncio.sleep(0.1)
        if random.random() < 0.6:  # 60% failure rate
            raise TemporaryUnavailableError("Service temporarily unavailable")
        return "Async success!"
    
    # Test synchronous retry
    try:
        result = flaky_function()
        print(f"Sync result: {result}")
    except Exception as e:
        print(f"Sync failed: {e}")
    
    # Test asynchronous retry
    async def test_async():
        try:
            result = await async_flaky_function()
            print(f"Async result: {result}")
        except Exception as e:
            print(f"Async failed: {e}")
    
    asyncio.run(test_async())
    
    # Test circuit breaker
    circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)
    
    def always_fail():
        raise ConnectionError("Always fails")
    
    # Trigger circuit breaker
    for i in range(6):
        try:
            circuit_breaker.call(always_fail)
        except Exception as e:
            print(f"Attempt {i+1}: {e}")
    
    print("Retry logic testing completed!")