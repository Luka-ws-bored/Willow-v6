"""
Cloud Sync System for Willow v6

This module provides cloud synchronization capabilities for memory data
and other persistent information across devices and services.
"""

import logging
import json
import os
import requests
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class CloudSync:
    """
    Cloud synchronization manager for Willow v6.
    
    Handles syncing memory data, configurations, and other persistent
    information with cloud services.
    """
    
    def __init__(self, config):
        self.endpoint = config.get('sync', {}).get('endpoint_url')
        self.token = config.get('sync', {}).get('token')
        self.headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}

    def sync(self, path: str) -> bool:
        """Upload a file or directory to the cloud sync endpoint."""
        if not self.endpoint:
            logger.error("CloudSync: No endpoint configured")
            return False
        url = f"{self.endpoint}/sync"
        files = {'file': open(path, 'rb')} if os.path.isfile(path) else None
        data = {'path': path}
        try:
            response = requests.post(url, headers=self.headers, files=files, data=data)
            response.raise_for_status()
            logger.info(f"CloudSync: {path} synced successfully.")
            return True
        except Exception as e:
            logger.error(f"CloudSync sync failed: {e}")
            return False

    def restore(self, path: str) -> bool:
        """Download a file or directory from the cloud sync endpoint."""
        if not self.endpoint:
            logger.error("CloudSync: No endpoint configured")
            return False
        try:
            response = requests.get(f"{self.endpoint}/restore", headers=self.headers, params={'path': path})
            response.raise_for_status()
            with open(path, 'wb') as f:
                f.write(response.content)
            logger.info(f"CloudSync: {path} restored successfully.")
            return True
        except Exception as e:
            logger.error(f"CloudSync restore failed: {e}")
            return False

    def list_devices(self) -> list:
        """List registered devices for sync."""
        if not self.endpoint:
            logger.error("CloudSync: No endpoint configured")
            return []
        try:
            resp = requests.get(f"{self.endpoint}/devices", headers=self.headers)
            resp.raise_for_status()
            devices = resp.json().get('devices', [])
            logger.info(f"CloudSync: Retrieved {len(devices)} devices.")
            return devices
        except Exception as e:
            logger.error(f"CloudSync list_devices failed: {e}")
            return []
    
    def sync_memory(self, memory_data: Dict[str, Any]) -> bool:
        """
        Sync memory data with cloud service.
        
        Args:
            memory_data: Memory data to sync
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            payload = {
                'type': 'memory_sync',
                'timestamp': datetime.now().isoformat(),
                'data': memory_data,
                'version': '6.0.0'
            }
            
            response = requests.post(
                f"{self.endpoint}/sync/memory",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Memory synced successfully with cloud.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Cloud sync failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during cloud sync: {e}")
            return False
    
    def sync_config(self, config_data: Dict[str, Any]) -> bool:
        """
        Sync configuration data with cloud service.
        
        Args:
            config_data: Configuration data to sync
            
        Returns:
            True if sync successful, False otherwise
        """
        try:
            payload = {
                'type': 'config_sync',
                'timestamp': datetime.now().isoformat(),
                'data': config_data,
                'version': '6.0.0'
            }
            
            response = requests.post(
                f"{self.endpoint}/sync/config",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            logger.info("Configuration synced successfully with cloud.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Config sync failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during config sync: {e}")
            return False
    
    def fetch_memory(self, device_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch memory data from cloud service.
        
        Args:
            device_id: Optional device identifier
            
        Returns:
            Memory data if successful, None otherwise
        """
        try:
            params = {}
            if device_id:
                params['device_id'] = device_id
            
            response = requests.get(
                f"{self.endpoint}/fetch/memory",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info("Memory data fetched successfully from cloud.")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Memory fetch failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during memory fetch: {e}")
            return None
    
    def fetch_config(self, device_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch configuration data from cloud service.
        
        Args:
            device_id: Optional device identifier
            
        Returns:
            Configuration data if successful, None otherwise
        """
        try:
            params = {}
            if device_id:
                params['device_id'] = device_id
            
            response = requests.get(
                f"{self.endpoint}/fetch/config",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info("Configuration data fetched successfully from cloud.")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Config fetch failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during config fetch: {e}")
            return None
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Get synchronization status from cloud service.
        
        Returns:
            Status information
        """
        try:
            response = requests.get(
                f"{self.endpoint}/status",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Status check failed: {e}")
            return {'status': 'offline', 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during status check: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def backup_data(self, data: Dict[str, Any], backup_type: str = 'manual') -> bool:
        """
        Create a backup of data in the cloud.
        
        Args:
            data: Data to backup
            backup_type: Type of backup (manual, auto, scheduled)
            
        Returns:
            True if backup successful, False otherwise
        """
        try:
            payload = {
                'type': 'backup',
                'backup_type': backup_type,
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'version': '6.0.0'
            }
            
            response = requests.post(
                f"{self.endpoint}/backup",
                json=payload,
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            
            logger.info(f"{backup_type.title()} backup created successfully.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Backup failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during backup: {e}")
            return False
    
    def restore_data(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore data from a cloud backup.
        
        Args:
            backup_id: ID of the backup to restore
            
        Returns:
            Restored data if successful, None otherwise
        """
        try:
            response = requests.get(
                f"{self.endpoint}/restore/{backup_id}",
                headers=self.headers,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Data restored successfully from backup {backup_id}.")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Restore failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during restore: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups in the cloud.
        
        Returns:
            List of backup information
        """
        try:
            response = requests.get(
                f"{self.endpoint}/backups",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {len(data)} backup(s) from cloud.")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Backup listing failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during backup listing: {e}")
            return []
    
    def close(self):
        """Close the cloud sync session."""
        logger.info("Cloud sync session closed.")


# Utility functions
def create_cloud_sync(endpoint_url: str, api_key: Optional[str] = None) -> CloudSync:
    """
    Create a cloud sync instance.
    
    Args:
        endpoint_url: Cloud sync endpoint URL
        api_key: Optional API key
        
    Returns:
        CloudSync instance
    """
    return CloudSync(endpoint_url, api_key)


def test_cloud_connection(endpoint_url: str, api_key: Optional[str] = None) -> bool:
    """
    Test cloud connection.
    
    Args:
        endpoint_url: Cloud sync endpoint URL
        api_key: Optional API key
        
    Returns:
        True if connection successful, False otherwise
    """
    try:
        sync = CloudSync(endpoint_url, api_key)
        status = sync.get_sync_status()
        sync.close()
        
        return status.get('status') != 'offline'
        
    except Exception as e:
        logger.error(f"Cloud connection test failed: {e}")
        return False 