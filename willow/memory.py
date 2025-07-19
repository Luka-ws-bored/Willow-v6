"""
Memory Persistence System for Willow v6

This module provides a simple JSON-based memory system for storing
conversation history, events, and other persistent data.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class MemoryManager:
    """
    Manages persistent memory storage using JSON files.
    
    Provides methods for loading, saving, and querying memory entries
    with automatic timestamping and file persistence.
    """
    
    def __init__(self, memory_file: str = "memory.json"):
        """
        Initialize the memory manager.
        
        Args:
            memory_file: Path to the JSON file for storing memory
        """
        self.memory_file = memory_file
        self.memory: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        
        # Load existing memory on initialization
        self.load_memory()
        self.logger.info(f"Memory manager initialized with file: {memory_file}")
    
    def load_memory(self) -> None:
        """
        Load memory entries from JSON file.
        
        Creates the file if it doesn't exist.
        """
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.memory = json.load(f)
                self.logger.info(f"Loaded {len(self.memory)} memory entries from {self.memory_file}")
            else:
                self.memory = []
                self.logger.info(f"Memory file {self.memory_file} not found, starting with empty memory")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding memory file {self.memory_file}: {e}")
            self.memory = []
        except Exception as e:
            self.logger.error(f"Error loading memory from {self.memory_file}: {e}")
            self.memory = []
    
    def save_memory(self) -> None:
        """
        Save memory entries to JSON file.
        
        Creates the file if it doesn't exist.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.memory_file) if os.path.dirname(self.memory_file) else '.', exist_ok=True)
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.memory)} memory entries to {self.memory_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving memory to {self.memory_file}: {e}")
            raise
    
    def add_entry(self, entry: Dict[str, Any]) -> None:
        """
        Add a new memory entry with automatic timestamping.
        
        Args:
            entry: Dictionary containing the memory entry data
        """
        # Add timestamp to entry
        entry_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **entry
        }
        
        self.memory.append(entry_with_timestamp)
        self.logger.debug(f"Added memory entry: {entry.get('event', 'Unknown event')}")
        
        # Auto-save after adding entry
        self.save_memory()
    
    def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent memory entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of recent memory entries (most recent first)
        """
        if limit <= 0:
            return []
        
        # Return the last 'limit' entries, reversed to show most recent first
        recent_entries = self.memory[-limit:][::-1]
        self.logger.debug(f"Retrieved {len(recent_entries)} recent memory entries")
        return recent_entries
    
    def get_entries_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all memory entries of a specific type.
        
        Args:
            event_type: Type of event to filter by
            
        Returns:
            List of memory entries matching the event type
        """
        filtered_entries = [
            entry for entry in self.memory 
            if entry.get('event') == event_type
        ]
        self.logger.debug(f"Retrieved {len(filtered_entries)} entries of type '{event_type}'")
        return filtered_entries
    
    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memory entries by text content.
        
        Args:
            query: Text to search for in memory entries
            
        Returns:
            List of memory entries containing the query
        """
        query_lower = query.lower()
        matching_entries = []
        
        for entry in self.memory:
            # Search in all string values of the entry
            entry_text = json.dumps(entry, ensure_ascii=False).lower()
            if query_lower in entry_text:
                matching_entries.append(entry)
        
        self.logger.debug(f"Found {len(matching_entries)} entries matching query '{query}'")
        return matching_entries
    
    def clear_memory(self) -> None:
        """
        Clear all memory entries and save empty file.
        """
        self.memory = []
        self.save_memory()
        self.logger.info("Memory cleared successfully")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary containing memory statistics
        """
        if not self.memory:
            return {
                "total_entries": 0,
                "file_size": 0,
                "oldest_entry": None,
                "newest_entry": None,
                "event_types": []
            }
        
        # Calculate statistics
        total_entries = len(self.memory)
        file_size = os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0
        
        # Get event types
        event_types = list(set(entry.get('event') for entry in self.memory if entry.get('event')))
        
        # Get oldest and newest entries
        timestamps = [entry.get('timestamp') for entry in self.memory if entry.get('timestamp')]
        oldest_entry = min(timestamps) if timestamps else None
        newest_entry = max(timestamps) if timestamps else None
        
        return {
            "total_entries": total_entries,
            "file_size": file_size,
            "oldest_entry": oldest_entry,
            "newest_entry": newest_entry,
            "event_types": event_types
        }
    
    def backup_memory(self, backup_file: Optional[str] = None) -> str:
        """
        Create a backup of the current memory.
        
        Args:
            backup_file: Optional backup file path. If None, generates timestamped filename.
            
        Returns:
            Path to the backup file
        """
        if backup_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"memory_backup_{timestamp}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Memory backed up to {backup_file}")
            return backup_file
            
        except Exception as e:
            self.logger.error(f"Error creating memory backup: {e}")
            raise
    
    def restore_memory(self, backup_file: str) -> None:
        """
        Restore memory from a backup file.
        
        Args:
            backup_file: Path to the backup file to restore from
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_memory = json.load(f)
            
            self.memory = backup_memory
            self.save_memory()
            self.logger.info(f"Memory restored from {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Error restoring memory from {backup_file}: {e}")
            raise 