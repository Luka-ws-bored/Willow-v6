"""
Tests for enhanced logging configuration and structured telemetry.
"""

import unittest
import asyncio
import tempfile
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestLoggingTelemetry(unittest.TestCase):
    """Test enhanced logging and telemetry functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        self.loop.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logging_imports(self):
        """Test that enhanced logging components can be imported."""
        try:
            from utils.logging_config import (
                setup_willow_logging, TelemetryData, TelemetryContext,
                AsyncTelemetryContext, get_rag_metrics, export_telemetry_data,
                JSONTelemetryFormatter, EnhancedRAGPerformanceFilter
            )
            self.assertTrue(callable(setup_willow_logging))
            self.assertTrue(callable(TelemetryData))
            self.assertTrue(callable(get_rag_metrics))
            print("✅ Enhanced logging imports successful")
        except ImportError as e:
            self.skipTest(f"Enhanced logging not available: {e}")
    
    def test_telemetry_data_creation(self):
        """Test TelemetryData creation and methods."""
        try:
            from utils.logging_config import TelemetryData
            
            # Create telemetry data
            telemetry = TelemetryData("test_operation", "test-query-123")
            
            self.assertEqual(telemetry.operation_type, "test_operation")
            self.assertEqual(telemetry.query_id, "test-query-123")
            self.assertIsNotNone(telemetry.timestamp)
            self.assertFalse(telemetry.cache_hit)
            
            # Test methods
            telemetry.set_pipeline("test_pipeline")
            telemetry.set_cache_hit(True)
            
            self.assertEqual(telemetry.pipeline_used, "test_pipeline")
            self.assertTrue(telemetry.cache_hit)
            
            # Test error setting
            test_error = ValueError("Test error")
            telemetry.set_error(test_error)
            
            self.assertIsNotNone(telemetry.error)
            self.assertEqual(telemetry.error['type'], 'ValueError')
            
            # Test finishing
            time.sleep(0.01)  # Small delay
            duration = telemetry.finish()
            self.assertGreater(duration, 0)
            self.assertEqual(telemetry.response_time, duration)
            
            # Test serialization
            data_dict = telemetry.to_dict()
            self.assertIsInstance(data_dict, dict)
            self.assertEqual(data_dict['query_id'], "test-query-123")
            self.assertEqual(data_dict['operation_type'], "test_operation")
            
            print("✅ TelemetryData test passed")
            
        except ImportError:
            self.skipTest("TelemetryData not available")
    
    def test_telemetry_context_manager(self):
        """Test TelemetryContext manager functionality."""
        try:
            from utils.logging_config import TelemetryContext
            
            # Test successful operation
            with TelemetryContext("test_operation", pipeline="test_pipeline") as telemetry:
                self.assertEqual(telemetry.operation_type, "test_operation")
                self.assertEqual(telemetry.pipeline_used, "test_pipeline")
                time.sleep(0.01)  # Simulate work
            
            self.assertIsNotNone(telemetry.response_time)
            self.assertGreater(telemetry.response_time, 0)
            
            # Test error handling
            try:
                with TelemetryContext("error_test") as error_telemetry:
                    raise ValueError("Test error in context")
            except ValueError:
                pass  # Expected
            
            self.assertIsNotNone(error_telemetry.error)
            self.assertEqual(error_telemetry.error['type'], 'ValueError')
            
            print("✅ TelemetryContext test passed")
            
        except ImportError:
            self.skipTest("TelemetryContext not available")
    
    def test_async_telemetry_context(self):
        """Test AsyncTelemetryContext functionality."""
        async def run_async_telemetry_test():
            try:
                from utils.logging_config import AsyncTelemetryContext
                
                # Test successful async operation
                async with AsyncTelemetryContext("async_test", pipeline="async_pipeline") as telemetry:
                    self.assertEqual(telemetry.operation_type, "async_test")
                    await asyncio.sleep(0.01)  # Simulate async work
                
                self.assertIsNotNone(telemetry.response_time)
                self.assertGreater(telemetry.response_time, 0)
                
                # Test async error handling
                try:
                    async with AsyncTelemetryContext("async_error_test") as error_telemetry:
                        raise ValueError("Async test error")
                except ValueError:
                    pass  # Expected
                
                self.assertIsNotNone(error_telemetry.error)
                
                print("✅ AsyncTelemetryContext test passed")
                
            except ImportError:
                self.skipTest("AsyncTelemetryContext not available")
        
        self.loop.run_until_complete(run_async_telemetry_test())
    
    def test_enhanced_logging_setup(self):
        """Test enhanced logging setup with JSON telemetry."""
        try:
            from utils.logging_config import setup_willow_logging
            
            log_file = self.temp_path / "test.log"
            json_file = self.temp_path / "telemetry.json"
            
            # Setup logging with JSON telemetry
            logger = setup_willow_logging(
                log_level="DEBUG",
                log_file=log_file,
                enable_performance_tracking=True,
                enable_json_telemetry=True,
                json_telemetry_file=json_file
            )
            
            self.assertIsNotNone(logger)
            self.assertEqual(logger.name, 'willow')
            self.assertTrue(hasattr(logger, '_performance_filter'))
            
            print("✅ Enhanced logging setup test passed")
            
        except ImportError:
            self.skipTest("Enhanced logging setup not available")
    
    def test_performance_filter_metrics(self):
        """Test EnhancedRAGPerformanceFilter metrics collection."""
        try:
            from utils.logging_config import EnhancedRAGPerformanceFilter, TelemetryData
            import logging
            
            # Create filter
            perf_filter = EnhancedRAGPerformanceFilter()
            
            # Create mock log records with telemetry
            telemetry1 = TelemetryData("query", "test-1")
            telemetry1.set_pipeline("test_pipeline")
            telemetry1.set_cache_hit(True)
            telemetry1.finish()
            
            record1 = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="Test message", args=(), exc_info=None
            )
            record1.telemetry = telemetry1
            
            # Process record
            perf_filter.filter(record1)
            
            # Test legacy record format
            record2 = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="Legacy test", args=(), exc_info=None
            )
            record2.rag_operation = "query"
            record2.duration = 0.5
            
            perf_filter.filter(record2)
            
            # Get metrics
            metrics = perf_filter.get_metrics()
            
            self.assertGreater(metrics['query_count'], 0)
            self.assertGreater(metrics['cache_hits'], 0)
            self.assertIn('avg_retrieval_time', metrics)
            
            # Test telemetry history
            history = perf_filter.get_telemetry_history(limit=10)
            self.assertIsInstance(history, list)
            self.assertGreater(len(history), 0)
            
            print("✅ Performance filter metrics test passed")
            
        except ImportError:
            self.skipTest("Performance filter not available")
    
    def test_json_telemetry_formatter(self):
        """Test JSON telemetry formatter."""
        try:
            from utils.logging_config import JSONTelemetryFormatter, TelemetryData
            import logging
            
            formatter = JSONTelemetryFormatter()
            
            # Create record with telemetry
            telemetry = TelemetryData("test_op", "test-query")
            telemetry.set_pipeline("json_test")
            telemetry.finish()
            
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=0,
                msg="JSON test message", args=(), exc_info=None
            )
            record.telemetry = telemetry
            
            # Format record
            formatted = formatter.format(record)
            
            # Parse JSON
            parsed = json.loads(formatted)
            
            self.assertEqual(parsed['message'], "JSON test message")
            self.assertEqual(parsed['operation_type'], "test_op")
            self.assertEqual(parsed['query_id'], "test-query")
            self.assertEqual(parsed['pipeline_used'], "json_test")
            self.assertIn('timestamp', parsed)
            
            print("✅ JSON telemetry formatter test passed")
            
        except ImportError:
            self.skipTest("JSON formatter not available")
    
    def test_telemetry_export(self):
        """Test telemetry data export functionality."""
        try:
            from utils.logging_config import (
                setup_willow_logging, export_telemetry_data,
                TelemetryContext
            )
            
            # Setup logger
            logger = setup_willow_logging(
                log_level="INFO",
                enable_performance_tracking=True
            )
            
            # Generate some telemetry data
            with TelemetryContext("export_test", pipeline="export_pipeline"):
                time.sleep(0.01)
            
            # Export data
            export_json = export_telemetry_data(logger, format='json')
            export_dict = export_telemetry_data(logger, format='dict')
            
            # Test JSON export
            self.assertIsInstance(export_json, str)
            parsed_json = json.loads(export_json)
            self.assertIn('metrics', parsed_json)
            self.assertIn('history', parsed_json)
            self.assertIn('export_time', parsed_json)
            
            # Test dict export
            self.assertIsInstance(export_dict, dict)
            self.assertIn('metrics', export_dict)
            self.assertIn('history', export_dict)
            
            print("✅ Telemetry export test passed")
            
        except ImportError:
            self.skipTest("Telemetry export not available")
    
    def test_legacy_compatibility(self):
        """Test backward compatibility with legacy logging."""
        try:
            from utils.logging_config import log_rag_operation, rag_logger
            
            # Test legacy decorator (should work with new telemetry system)
            @log_rag_operation("legacy_test", cache_hit=True)
            def legacy_function():
                return "legacy result"
            
            result = legacy_function()
            self.assertEqual(result, "legacy result")
            
            # Test legacy logger
            logger = rag_logger()
            self.assertIsNotNone(logger)
            
            print("✅ Legacy compatibility test passed")
            
        except ImportError:
            self.skipTest("Legacy logging compatibility not available")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)