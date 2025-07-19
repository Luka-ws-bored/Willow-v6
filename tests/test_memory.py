"""
Unit tests for the Memory Persistence System

Tests the MemoryManager class functionality including loading, saving,
adding entries, retrieving recent entries, and clearing memory.
"""

import unittest
import json
import tempfile
import os
import shutil
from datetime import datetime
from unittest.mock import patch, mock_open

# Add the parent directory to the path to import willow modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from willow.memory import MemoryManager


class TestMemoryManager(unittest.TestCase):
    """Test cases for the MemoryManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_memory_file = os.path.join(self.test_dir, "test_memory.json")
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove temporary directory and files
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init_with_default_file(self):
        """Test MemoryManager initialization with default file."""
        with patch('os.path.exists', return_value=False):
            memory = MemoryManager()
            self.assertEqual(memory.memory_file, "memory.json")
            self.assertEqual(memory.memory, [])
    
    def test_init_with_custom_file(self):
        """Test MemoryManager initialization with custom file."""
        memory = MemoryManager(self.test_memory_file)
        self.assertEqual(memory.memory_file, self.test_memory_file)
        self.assertEqual(memory.memory, [])
    
    def test_load_memory_new_file(self):
        """Test loading memory from a non-existent file."""
        memory = MemoryManager(self.test_memory_file)
        self.assertEqual(memory.memory, [])
    
    def test_load_memory_existing_file(self):
        """Test loading memory from an existing file."""
        # Create test data
        test_data = [
            {"timestamp": "2024-01-01T10:00:00", "event": "test1", "data": "value1"},
            {"timestamp": "2024-01-01T11:00:00", "event": "test2", "data": "value2"}
        ]
        
        # Write test data to file
        with open(self.test_memory_file, 'w') as f:
            json.dump(test_data, f)
        
        # Load memory
        memory = MemoryManager(self.test_memory_file)
        self.assertEqual(len(memory.memory), 2)
        self.assertEqual(memory.memory[0]["event"], "test1")
        self.assertEqual(memory.memory[1]["event"], "test2")
    
    def test_load_memory_invalid_json(self):
        """Test loading memory from a file with invalid JSON."""
        # Write invalid JSON to file
        with open(self.test_memory_file, 'w') as f:
            f.write("invalid json content")
        
        # Load memory should handle the error gracefully
        memory = MemoryManager(self.test_memory_file)
        self.assertEqual(memory.memory, [])
    
    def test_save_memory(self):
        """Test saving memory to file."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add some test data
        test_entry = {"event": "test_save", "data": "test_value"}
        memory.memory.append(test_entry)
        
        # Save memory
        memory.save_memory()
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.test_memory_file))
        
        with open(self.test_memory_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(len(saved_data), 1)
        self.assertEqual(saved_data[0]["event"], "test_save")
    
    def test_add_entry(self):
        """Test adding a new memory entry."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add entry
        entry = {"event": "test_event", "data": "test_data"}
        memory.add_entry(entry)
        
        # Verify entry was added with timestamp
        self.assertEqual(len(memory.memory), 1)
        self.assertIn("timestamp", memory.memory[0])
        self.assertEqual(memory.memory[0]["event"], "test_event")
        self.assertEqual(memory.memory[0]["data"], "test_data")
        
        # Verify file was saved
        self.assertTrue(os.path.exists(self.test_memory_file))
    
    def test_add_entry_timestamp_format(self):
        """Test that added entries have proper timestamp format."""
        memory = MemoryManager(self.test_memory_file)
        
        entry = {"event": "test_timestamp"}
        memory.add_entry(entry)
        
        # Check timestamp format (ISO format)
        timestamp = memory.memory[0]["timestamp"]
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            self.fail("Timestamp is not in valid ISO format")
    
    def test_get_recent_empty_memory(self):
        """Test getting recent entries from empty memory."""
        memory = MemoryManager(self.test_memory_file)
        
        recent = memory.get_recent(5)
        self.assertEqual(recent, [])
    
    def test_get_recent_with_entries(self):
        """Test getting recent entries from memory with data."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add multiple entries
        for i in range(10):
            memory.add_entry({"event": f"event_{i}", "index": i})
        
        # Get recent entries
        recent = memory.get_recent(5)
        
        # Should return 5 entries, most recent first
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[0]["event"], "event_9")  # Most recent
        self.assertEqual(recent[4]["event"], "event_5")  # Least recent of the 5
    
    def test_get_recent_limit_exceeds_entries(self):
        """Test getting recent entries when limit exceeds available entries."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add 3 entries
        for i in range(3):
            memory.add_entry({"event": f"event_{i}"})
        
        # Request 10 recent entries
        recent = memory.get_recent(10)
        
        # Should return all 3 entries, most recent first
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0]["event"], "event_2")
        self.assertEqual(recent[2]["event"], "event_0")
    
    def test_get_recent_zero_limit(self):
        """Test getting recent entries with zero limit."""
        memory = MemoryManager(self.test_memory_file)
        
        memory.add_entry({"event": "test"})
        recent = memory.get_recent(0)
        
        self.assertEqual(recent, [])
    
    def test_get_recent_negative_limit(self):
        """Test getting recent entries with negative limit."""
        memory = MemoryManager(self.test_memory_file)
        
        memory.add_entry({"event": "test"})
        recent = memory.get_recent(-5)
        
        self.assertEqual(recent, [])
    
    def test_get_entries_by_type(self):
        """Test filtering entries by event type."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add entries with different event types
        memory.add_entry({"event": "plugin_loaded", "plugin": "test_plugin"})
        memory.add_entry({"event": "user_input", "input": "hello"})
        memory.add_entry({"event": "plugin_loaded", "plugin": "another_plugin"})
        memory.add_entry({"event": "error", "error": "test_error"})
        
        # Get plugin_loaded entries
        plugin_entries = memory.get_entries_by_type("plugin_loaded")
        self.assertEqual(len(plugin_entries), 2)
        self.assertEqual(plugin_entries[0]["plugin"], "test_plugin")
        self.assertEqual(plugin_entries[1]["plugin"], "another_plugin")
        
        # Get user_input entries
        input_entries = memory.get_entries_by_type("user_input")
        self.assertEqual(len(input_entries), 1)
        self.assertEqual(input_entries[0]["input"], "hello")
    
    def test_search_entries(self):
        """Test searching entries by text content."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add entries with different content
        memory.add_entry({"event": "plugin_loaded", "plugin": "color_mapper"})
        memory.add_entry({"event": "user_input", "input": "What color is the sky?"})
        memory.add_entry({"event": "response", "response": "The sky is blue"})
        
        # Search for "color"
        color_entries = memory.search_entries("color")
        self.assertEqual(len(color_entries), 2)  # color_mapper and "What color is the sky?"
        
        # Search for "blue"
        blue_entries = memory.search_entries("blue")
        self.assertEqual(len(blue_entries), 1)
        self.assertEqual(blue_entries[0]["response"], "The sky is blue")
    
    def test_clear_memory(self):
        """Test clearing all memory entries."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add some entries
        memory.add_entry({"event": "test1"})
        memory.add_entry({"event": "test2"})
        
        # Verify entries exist
        self.assertEqual(len(memory.memory), 2)
        self.assertTrue(os.path.exists(self.test_memory_file))
        
        # Clear memory
        memory.clear_memory()
        
        # Verify memory is cleared
        self.assertEqual(len(memory.memory), 0)
        
        # Verify file is saved with empty content
        with open(self.test_memory_file, 'r') as f:
            saved_data = json.load(f)
        self.assertEqual(saved_data, [])
    
    def test_get_memory_stats_empty(self):
        """Test getting memory statistics for empty memory."""
        memory = MemoryManager(self.test_memory_file)
        
        stats = memory.get_memory_stats()
        
        self.assertEqual(stats["total_entries"], 0)
        self.assertEqual(stats["file_size"], 0)
        self.assertIsNone(stats["oldest_entry"])
        self.assertIsNone(stats["newest_entry"])
        self.assertEqual(stats["event_types"], [])
    
    def test_get_memory_stats_with_entries(self):
        """Test getting memory statistics with entries."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add entries
        memory.add_entry({"event": "plugin_loaded", "plugin": "test"})
        memory.add_entry({"event": "user_input", "input": "hello"})
        memory.add_entry({"event": "plugin_loaded", "plugin": "another"})
        
        stats = memory.get_memory_stats()
        
        self.assertEqual(stats["total_entries"], 3)
        self.assertGreater(stats["file_size"], 0)
        self.assertIsNotNone(stats["oldest_entry"])
        self.assertIsNotNone(stats["newest_entry"])
        self.assertEqual(set(stats["event_types"]), {"plugin_loaded", "user_input"})
    
    def test_backup_memory(self):
        """Test creating a memory backup."""
        memory = MemoryManager(self.test_memory_file)
        
        # Add some entries
        memory.add_entry({"event": "test_backup", "data": "backup_test"})
        
        # Create backup
        backup_file = os.path.join(self.test_dir, "backup.json")
        created_backup = memory.backup_memory(backup_file)
        
        # Verify backup file was created
        self.assertEqual(created_backup, backup_file)
        self.assertTrue(os.path.exists(backup_file))
        
        # Verify backup contains correct data
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
        
        self.assertEqual(len(backup_data), 1)
        self.assertEqual(backup_data[0]["event"], "test_backup")
    
    def test_backup_memory_auto_filename(self):
        """Test creating a memory backup with auto-generated filename."""
        memory = MemoryManager(self.test_memory_file)
        
        memory.add_entry({"event": "test"})
        
        # Create backup with auto filename
        backup_file = memory.backup_memory()
        
        # Verify backup file was created with timestamp
        self.assertTrue(os.path.exists(backup_file))
        self.assertIn("memory_backup_", backup_file)
        self.assertTrue(backup_file.endswith(".json"))
    
    def test_restore_memory(self):
        """Test restoring memory from backup."""
        memory = MemoryManager(self.test_memory_file)
        
        # Create backup with some data
        backup_file = os.path.join(self.test_dir, "restore_backup.json")
        backup_data = [
            {"timestamp": "2024-01-01T10:00:00", "event": "restored_event", "data": "restored_data"}
        ]
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f)
        
        # Restore from backup
        memory.restore_memory(backup_file)
        
        # Verify memory was restored
        self.assertEqual(len(memory.memory), 1)
        self.assertEqual(memory.memory[0]["event"], "restored_event")
        self.assertEqual(memory.memory[0]["data"], "restored_data")
        
        # Verify file was saved
        self.assertTrue(os.path.exists(self.test_memory_file))


if __name__ == '__main__':
    unittest.main() 