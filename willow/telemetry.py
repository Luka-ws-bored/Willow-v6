"""
Telemetry System for Willow v6

This module provides telemetry and analytics collection capabilities
for monitoring usage patterns and system performance.
"""

import logging
import requests
import platform
import time
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TelemetryEvent:
    """Data class for telemetry events."""
    event_name: str
    timestamp: float
    session_id: str
    user_id: Optional[str]
    data: Dict[str, Any]
    system_info: Dict[str, str]
    version: str = "6.0.0"


class Telemetry:
    """
    Telemetry collection and reporting system for Willow v6.
    
    Collects usage analytics, performance metrics, and system information
    for monitoring and improvement purposes.
    """
    
    def __init__(self, telemetry_endpoint: str, api_key: Optional[str] = None):
        """
        Initialize telemetry system.
        
        Args:
            telemetry_endpoint: Telemetry endpoint URL
            api_key: Optional API key for authentication
        """
        self.telemetry_endpoint = telemetry_endpoint.rstrip('/')
        self.api_key = api_key
        self.session_id = str(uuid.uuid4())
        self.user_id = None
        self.session = requests.Session()
        
        # Set up headers
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
        
        # Collect system information
        self.system_info = self._collect_system_info()
        
        logger.info(f"Telemetry initialized with endpoint: {telemetry_endpoint}")
    
    def _collect_system_info(self) -> Dict[str, str]:
        """
        Collect system information for telemetry.
        
        Returns:
            Dictionary of system information
        """
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
        }
    
    def set_user_id(self, user_id: str):
        """
        Set user identifier for telemetry events.
        
        Args:
            user_id: User identifier
        """
        self.user_id = user_id
        logger.info(f"User ID set for telemetry: {user_id}")
    
    def send_event(self, event_name: str, data: Dict[str, Any], 
                   immediate: bool = True) -> bool:
        """
        Send a telemetry event.
        
        Args:
            event_name: Name of the event
            data: Event data
            immediate: Whether to send immediately or batch
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            event = TelemetryEvent(
                event_name=event_name,
                timestamp=time.time(),
                session_id=self.session_id,
                user_id=self.user_id,
                data=data,
                system_info=self.system_info
            )
            
            if immediate:
                return self._send_single_event(event)
            else:
                # TODO: Implement batching for non-immediate events
                return self._send_single_event(event)
                
        except Exception as e:
            logger.error(f"Failed to create telemetry event: {e}")
            return False
    
    def _send_single_event(self, event: TelemetryEvent) -> bool:
        """
        Send a single telemetry event.
        
        Args:
            event: Telemetry event to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            payload = asdict(event)
            
            response = self.session.post(
                f"{self.telemetry_endpoint}/event",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.debug(f"Telemetry event '{event.event_name}' sent successfully.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send telemetry event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending telemetry event: {e}")
            return False
    
    def track_plugin_usage(self, plugin_name: str, success: bool, 
                          execution_time: Optional[float] = None) -> bool:
        """
        Track plugin usage for analytics.
        
        Args:
            plugin_name: Name of the plugin used
            success: Whether the plugin execution was successful
            execution_time: Execution time in seconds
            
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'plugin_name': plugin_name,
            'success': success,
            'execution_time': execution_time,
            'category': 'plugin_usage'
        }
        
        return self.send_event('plugin_used', data)
    
    def track_feature_usage(self, feature_name: str, action: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track feature usage for analytics.
        
        Args:
            feature_name: Name of the feature used
            action: Action performed (e.g., 'clicked', 'enabled', 'disabled')
            metadata: Additional metadata
            
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'feature_name': feature_name,
            'action': action,
            'metadata': metadata or {},
            'category': 'feature_usage'
        }
        
        return self.send_event('feature_used', data)
    
    def track_error(self, error_type: str, error_message: str, 
                   context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track errors for monitoring and debugging.
        
        Args:
            error_type: Type of error
            error_message: Error message
            context: Additional context information
            
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {},
            'category': 'error_tracking'
        }
        
        return self.send_event('error_occurred', data)
    
    def track_performance(self, operation: str, duration: float, 
                         success: bool, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Track performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether the operation was successful
            metadata: Additional metadata
            
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'operation': operation,
            'duration': duration,
            'success': success,
            'metadata': metadata or {},
            'category': 'performance'
        }
        
        return self.send_event('performance_metric', data)
    
    def track_session_start(self) -> bool:
        """
        Track session start event.
        
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'session_duration': 0,
            'category': 'session'
        }
        
        return self.send_event('session_started', data)
    
    def track_session_end(self, session_duration: float) -> bool:
        """
        Track session end event.
        
        Args:
            session_duration: Session duration in seconds
            
        Returns:
            True if tracked successfully, False otherwise
        """
        data = {
            'session_duration': session_duration,
            'category': 'session'
        }
        
        return self.send_event('session_ended', data)
    
    def send_heartbeat(self) -> bool:
        """
        Send heartbeat to indicate system is active.
        
        Returns:
            True if sent successfully, False otherwise
        """
        data = {
            'uptime': time.time(),
            'category': 'system'
        }
        
        return self.send_event('heartbeat', data)
    
    def get_telemetry_status(self) -> Dict[str, Any]:
        """
        Get telemetry system status.
        
        Returns:
            Status information
        """
        try:
            response = self.session.get(
                f"{self.telemetry_endpoint}/status",
                timeout=5
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Telemetry status check failed: {e}")
            return {'status': 'offline', 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during telemetry status check: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def close(self):
        """Close the telemetry session."""
        self.session.close()
        logger.info("Telemetry session closed.")


# Utility functions
def create_telemetry(endpoint_url: str, api_key: Optional[str] = None) -> Telemetry:
    """
    Create a telemetry instance.
    
    Args:
        endpoint_url: Telemetry endpoint URL
        api_key: Optional API key
        
    Returns:
        Telemetry instance
    """
    return Telemetry(endpoint_url, api_key)


def test_telemetry_connection(endpoint_url: str, api_key: Optional[str] = None) -> bool:
    """
    Test telemetry connection.
    
    Args:
        endpoint_url: Telemetry endpoint URL
        api_key: Optional API key
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        telemetry = Telemetry(endpoint_url, api_key)
        status = telemetry.get_telemetry_status()
        telemetry.close()
        
        return status.get('status') != 'offline'
        
    except Exception as e:
        logger.error(f"Telemetry connection test failed: {e}")
        return False 