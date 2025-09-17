"""
Enhanced logging configuration for Willow v6 with RAG integration.
Provides centralized logging setup with performance tracking.
"""

import logging
import logging.handlers
import sys
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from functools import wraps


class TelemetryData:
    """Structured telemetry data for RAG operations."""
    
    def __init__(self, operation_type: str, query_id: Optional[str] = None):
        self.query_id = query_id or str(uuid.uuid4())
        self.operation_type = operation_type
        self.timestamp = datetime.utcnow().isoformat()
        self.pipeline_used = None
        self.start_time = time.perf_counter()
        self.response_time = None
        self.cache_hit = False
        self.error = None
        self.metadata = {}
    
    def set_pipeline(self, pipeline_name: str):
        """Set the pipeline used for this operation."""
        self.pipeline_used = pipeline_name
    
    def set_cache_hit(self, hit: bool):
        """Set whether this was a cache hit."""
        self.cache_hit = hit
    
    def set_error(self, error: Exception):
        """Set error information."""
        self.error = {
            'type': type(error).__name__,
            'message': str(error)
        }
    
    def finish(self) -> float:
        """Mark operation as finished and return duration."""
        self.response_time = time.perf_counter() - self.start_time
        return self.response_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'query_id': self.query_id,
            'operation_type': self.operation_type,
            'timestamp': self.timestamp,
            'pipeline_used': self.pipeline_used,
            'response_time': self.response_time,
            'cache_hit': self.cache_hit,
            'error': self.error,
            'metadata': self.metadata
        }


class JSONTelemetryFormatter(logging.Formatter):
    """JSON formatter for structured telemetry logging."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        
        # Add telemetry data if present
        if hasattr(record, 'telemetry') and isinstance(record.telemetry, TelemetryData):
            log_data.update(record.telemetry.to_dict())
        
        # Add RAG-specific fields for backward compatibility
        if hasattr(record, 'rag_operation'):
            log_data['rag_operation'] = record.rag_operation
        if hasattr(record, 'duration'):
            log_data['response_time'] = record.duration
        if hasattr(record, 'cache_hit'):
            log_data['cache_hit'] = record.cache_hit
        if hasattr(record, 'query_id'):
            log_data['query_id'] = record.query_id
        
        return json.dumps(log_data, separators=(',', ':'))


class EnhancedRAGPerformanceFilter(logging.Filter):
    """Enhanced filter to track RAG-specific performance metrics with structured telemetry."""
    
    def __init__(self):
        super().__init__()
        self.rag_metrics: Dict[str, Any] = {
            'query_count': 0,
            'retrieval_times': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'vector_db_operations': 0,
            'errors': 0,
            'pipeline_usage': {},
            'error_types': {},
            'total_response_time': 0.0
        }
        self.telemetry_history: List[Dict[str, Any]] = []
    
    def filter(self, record):
        # Track enhanced telemetry
        if hasattr(record, 'telemetry') and isinstance(record.telemetry, TelemetryData):
            telemetry = record.telemetry
            
            # Update metrics
            if telemetry.operation_type == 'query':
                self.rag_metrics['query_count'] += 1
                if telemetry.response_time:
                    self.rag_metrics['retrieval_times'].append(telemetry.response_time)
                    self.rag_metrics['total_response_time'] += telemetry.response_time
            
            if telemetry.cache_hit:
                self.rag_metrics['cache_hits'] += 1
            else:
                self.rag_metrics['cache_misses'] += 1
            
            if telemetry.pipeline_used:
                pipeline = telemetry.pipeline_used
                self.rag_metrics['pipeline_usage'][pipeline] = self.rag_metrics['pipeline_usage'].get(pipeline, 0) + 1
            
            if telemetry.error:
                self.rag_metrics['errors'] += 1
                error_type = telemetry.error['type']
                self.rag_metrics['error_types'][error_type] = self.rag_metrics['error_types'].get(error_type, 0) + 1
            
            # Store telemetry for history (keep last 1000)
            self.telemetry_history.append(telemetry.to_dict())
            if len(self.telemetry_history) > 1000:
                self.telemetry_history.pop(0)
        
        # Legacy RAG operation tracking
        if hasattr(record, 'rag_operation'):
            if record.rag_operation == 'query':
                self.rag_metrics['query_count'] += 1
            elif record.rag_operation == 'cache_hit':
                self.rag_metrics['cache_hits'] += 1
            elif record.rag_operation == 'vector_db':
                self.rag_metrics['vector_db_operations'] += 1
            elif record.rag_operation == 'error':
                self.rag_metrics['errors'] += 1
            
            if hasattr(record, 'duration'):
                self.rag_metrics['retrieval_times'].append(record.duration)
                self.rag_metrics['total_response_time'] += record.duration
        
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive RAG performance metrics."""
        metrics = self.rag_metrics.copy()
        
        if self.rag_metrics['retrieval_times']:
            times = self.rag_metrics['retrieval_times']
            metrics['avg_retrieval_time'] = sum(times) / len(times)
            metrics['max_retrieval_time'] = max(times)
            metrics['min_retrieval_time'] = min(times)
            metrics['p95_retrieval_time'] = sorted(times)[int(len(times) * 0.95)] if len(times) > 20 else max(times)
        
        total_cache_operations = self.rag_metrics['cache_hits'] + self.rag_metrics['cache_misses']
        if total_cache_operations > 0:
            metrics['cache_hit_rate'] = self.rag_metrics['cache_hits'] / total_cache_operations
        
        if self.rag_metrics['query_count'] > 0:
            metrics['error_rate'] = self.rag_metrics['errors'] / self.rag_metrics['query_count']
            metrics['avg_total_response_time'] = self.rag_metrics['total_response_time'] / self.rag_metrics['query_count']
        
        return metrics
    
    def get_telemetry_history(self, limit: int = 100) -> list:
        """Get recent telemetry history."""
        return self.telemetry_history[-limit:] if limit else self.telemetry_history.copy()


class WillowFormatter(logging.Formatter):
    """Custom formatter for Willow with enhanced RAG information."""
    
    def __init__(self, include_performance=True):
        super().__init__()
        self.include_performance = include_performance
    
    def format(self, record):
        # Base format
        log_format = "%(asctime)s - %(name)s - %(levelname)s"
        
        # Add RAG context if available
        if hasattr(record, 'rag_operation'):
            log_format += " - RAG:%(rag_operation)s"
        
        if hasattr(record, 'duration') and self.include_performance:
            log_format += " - Duration:%(duration).3fs"
        
        if hasattr(record, 'cache_hit'):
            log_format += " - Cache:%(cache_hit)s"
        
        log_format += " - %(message)s"
        
        formatter = logging.Formatter(log_format)
        return formatter.format(record)


def setup_willow_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    enable_performance_tracking: bool = True,
    enable_json_telemetry: bool = False,
    json_telemetry_file: Optional[Path] = None,
    max_log_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up comprehensive logging for Willow v6 with RAG integration and structured telemetry.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        enable_performance_tracking: Whether to enable performance tracking
        enable_json_telemetry: Whether to enable JSON structured telemetry
        json_telemetry_file: Optional separate JSON telemetry file
        max_log_size: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured logger instance
    """
    # Create main logger
    logger = logging.getLogger('willow')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = WillowFormatter(include_performance=enable_performance_tracking)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation if specified
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_log_size,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add performance filter if enabled
    if enable_performance_tracking:
        perf_filter = EnhancedRAGPerformanceFilter()
        logger.addFilter(perf_filter)
        
        # Store filter reference for metrics access
        logger._performance_filter = perf_filter
    
    # Add JSON telemetry handler if enabled
    if enable_json_telemetry:
        json_formatter = JSONTelemetryFormatter()
        
        if json_telemetry_file:
            # Separate JSON telemetry file
            json_telemetry_file = Path(json_telemetry_file)
            json_telemetry_file.parent.mkdir(parents=True, exist_ok=True)
            
            json_handler = logging.handlers.RotatingFileHandler(
                json_telemetry_file,
                maxBytes=max_log_size,
                backupCount=backup_count
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(json_formatter)
            
            # Create separate logger for JSON telemetry
            json_logger = logging.getLogger('willow.telemetry')
            json_logger.setLevel(logging.DEBUG)
            json_logger.addHandler(json_handler)
            
            # Store reference
            logger._json_logger = json_logger
        else:
            # Add JSON handler to main logger
            json_console_handler = logging.StreamHandler(sys.stderr)
            json_console_handler.setLevel(logging.INFO)
            json_console_handler.setFormatter(json_formatter)
            json_console_handler.addFilter(
                lambda record: hasattr(record, 'telemetry') or hasattr(record, 'rag_operation')
            )
            logger.addHandler(json_console_handler)
    
    return logger


def create_telemetry_context(operation_type: str, query_id: Optional[str] = None, pipeline: Optional[str] = None) -> TelemetryData:
    """Create a telemetry context for tracking RAG operations."""
    telemetry = TelemetryData(operation_type, query_id)
    if pipeline:
        telemetry.set_pipeline(pipeline)
    return telemetry


def log_telemetry(telemetry: TelemetryData, message: str, level: str = "INFO"):
    """Log telemetry data with structured information."""
    logger = logging.getLogger('willow.rag')
    
    # Get the logging method
    log_method = getattr(logger, level.lower())
    
    # Log with telemetry context
    log_method(
        message,
        extra={
            'telemetry': telemetry,
            'query_id': telemetry.query_id,
            'rag_operation': telemetry.operation_type,
            'duration': telemetry.response_time,
            'cache_hit': telemetry.cache_hit
        }
    )
    
    # Also log to JSON telemetry logger if available
    main_logger = logging.getLogger('willow')
    if hasattr(main_logger, '_json_logger'):
        main_logger._json_logger.info(message, extra={'telemetry': telemetry})


class TelemetryContext:
    """Context manager for structured telemetry tracking."""
    
    def __init__(self, operation_type: str, query_id: Optional[str] = None, pipeline: Optional[str] = None):
        self.telemetry = create_telemetry_context(operation_type, query_id, pipeline)
        self.logger = logging.getLogger('willow.rag')
    
    def __enter__(self) -> TelemetryData:
        return self.telemetry
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = self.telemetry.finish()
        
        if exc_type is None:
            log_telemetry(self.telemetry, f"{self.telemetry.operation_type} completed successfully")
        else:
            self.telemetry.set_error(exc_val)
            log_telemetry(self.telemetry, f"{self.telemetry.operation_type} failed: {exc_val}", "ERROR")


class AsyncTelemetryContext:
    """Async context manager for structured telemetry tracking."""
    
    def __init__(self, operation_type: str, query_id: Optional[str] = None, pipeline: Optional[str] = None):
        self.telemetry = create_telemetry_context(operation_type, query_id, pipeline)
        self.logger = logging.getLogger('willow.rag')
    
    async def __aenter__(self) -> TelemetryData:
        return self.telemetry
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = self.telemetry.finish()
        
        if exc_type is None:
            log_telemetry(self.telemetry, f"{self.telemetry.operation_type} completed successfully")
        else:
            self.telemetry.set_error(exc_val)
            log_telemetry(self.telemetry, f"{self.telemetry.operation_type} failed: {exc_val}", "ERROR")
def log_rag_operation(operation: str, cache_hit: bool = False, query_id: str = None, pipeline: str = None):
    """
    Decorator to log RAG operations with performance tracking (legacy support).
    
    Args:
        operation: Type of RAG operation (query, retrieval, etc.)
        cache_hit: Whether this was a cache hit
        query_id: Optional query identifier
        pipeline: Optional pipeline name
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use new telemetry context
            with TelemetryContext(operation, query_id, pipeline) as telemetry:
                telemetry.set_cache_hit(cache_hit)
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def log_async_rag_operation(operation: str, cache_hit: bool = False, query_id: str = None, pipeline: str = None):
    """
    Async decorator for logging RAG operations with structured telemetry.
    
    Args:
        operation: Type of RAG operation
        cache_hit: Whether this was a cache hit
        query_id: Optional query identifier
        pipeline: Optional pipeline name
    
    Returns:
        AsyncTelemetryContext instance
    """
    return AsyncTelemetryContext(operation, query_id, pipeline)


def get_rag_metrics(logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    """Get comprehensive RAG performance metrics from logger."""
    if logger is None:
        logger = logging.getLogger('willow')
    
    if hasattr(logger, '_performance_filter'):
        return logger._performance_filter.get_metrics()
    else:
        return {'error': 'Performance tracking not enabled'}


def get_telemetry_history(logger: Optional[logging.Logger] = None, limit: int = 100) -> list:
    """Get recent telemetry history."""
    if logger is None:
        logger = logging.getLogger('willow')
    
    if hasattr(logger, '_performance_filter'):
        return logger._performance_filter.get_telemetry_history(limit)
    else:
        return []


def export_telemetry_data(logger: Optional[logging.Logger] = None, format: str = 'json') -> Union[str, Dict]:
    """Export telemetry data in specified format."""
    if logger is None:
        logger = logging.getLogger('willow')
    
    metrics = get_rag_metrics(logger)
    history = get_telemetry_history(logger, limit=1000)
    
    export_data = {
        'metrics': metrics,
        'history': history,
        'export_time': datetime.utcnow().isoformat(),
        'total_operations': len(history)
    }
    
    if format.lower() == 'json':
        return json.dumps(export_data, indent=2)
    else:
        return export_data


def log_missing_dependencies(missing_deps: list, component: str = "RAG"):
    """
    Log missing dependencies with appropriate warning level.
    
    Args:
        missing_deps: List of missing dependency names
        component: Component name for context
    """
    logger = logging.getLogger('willow.dependencies')
    
    if missing_deps:
        logger.warning(
            f"{component} dependencies missing: {', '.join(missing_deps)}. "
            f"Install with: pip install {' '.join(missing_deps)}",
            extra={'rag_operation': 'dependency_check'}
        )
    else:
        logger.info(
            f"{component} dependencies satisfied",
            extra={'rag_operation': 'dependency_check'}
        )


# Global logger instance
_willow_logger = None

def get_willow_logger(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json_telemetry: bool = False,
    json_telemetry_file: Optional[str] = None
) -> logging.Logger:
    """
    Get or create the global Willow logger instance with enhanced telemetry.
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
        enable_json_telemetry: Whether to enable JSON structured telemetry
        json_telemetry_file: Optional JSON telemetry file path
    
    Returns:
        Configured logger instance
    """
    global _willow_logger
    
    if _willow_logger is None:
        log_path = None
        if log_file:
            log_path = Path(log_file)
        
        json_path = None
        if json_telemetry_file:
            json_path = Path(json_telemetry_file)
        
        _willow_logger = setup_willow_logging(
            log_level=log_level,
            log_file=log_path,
            enable_performance_tracking=True,
            enable_json_telemetry=enable_json_telemetry,
            json_telemetry_file=json_path
        )
    
    return _willow_logger


# Convenience function for RAG logging
def rag_logger() -> logging.Logger:
    """Get RAG-specific logger."""
    return logging.getLogger('willow.rag')


if __name__ == "__main__":
    # Test the enhanced logging configuration
    logger = setup_willow_logging(
        log_level="DEBUG",
        log_file=Path("test_willow.log"),
        enable_performance_tracking=True,
        enable_json_telemetry=True,
        json_telemetry_file=Path("test_willow_telemetry.json")
    )
    
    # Test basic logging
    logger.info("Testing enhanced Willow logging configuration")
    
    # Test structured telemetry
    print("Testing structured telemetry...")
    with TelemetryContext("test_query", pipeline="test_pipeline") as telemetry:
        time.sleep(0.1)  # Simulate work
        telemetry.set_cache_hit(True)
        telemetry.metadata["test_data"] = "sample_value"
    
    # Test async telemetry
    import asyncio
    
    async def test_async_telemetry():
        async with AsyncTelemetryContext("async_test_query", pipeline="async_pipeline") as telemetry:
            await asyncio.sleep(0.05)  # Simulate async work
            telemetry.set_cache_hit(False)
    
    asyncio.run(test_async_telemetry())
    
    # Test legacy RAG-specific logging
    rag_log = rag_logger()
    rag_log.info(
        "Testing legacy RAG operation logging",
        extra={
            'rag_operation': 'test',
            'duration': 0.123,
            'cache_hit': True,
            'query_id': 'test-123'
        }
    )
    
    # Get and display metrics
    metrics = get_rag_metrics(logger)
    print(f"\nRAG Metrics: {json.dumps(metrics, indent=2)}")
    
    # Get telemetry history
    history = get_telemetry_history(logger, limit=10)
    print(f"\nTelemetry History ({len(history)} entries):")
    for entry in history:
        print(f"  {entry['timestamp']}: {entry['operation_type']} - {entry['response_time']:.3f}s")
    
    # Export telemetry data
    export_data = export_telemetry_data(logger)
    print(f"\nExported telemetry data: {len(export_data)} characters")
    
    print("\nEnhanced logging configuration test completed!")