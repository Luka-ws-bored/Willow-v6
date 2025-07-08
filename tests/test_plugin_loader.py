"""
Unit tests for the dynamic plugin loading system.

Tests the load_plugins function and related utilities with mocked plugins.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from willow.plugin_loader import load_plugins, get_plugin_info, validate_plugin


class TestPluginLoader(unittest.TestCase):
    """Test cases for the plugin loading system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_config = """
active_plugins:
  - color_mood_mapper
  - bug_buster
  - sql_sorcerer
  - prompt_checker
"""
        
        self.empty_config = """
active_plugins: []
"""
        
        self.no_plugins_config = """
version: 6.0.0
# No active_plugins section
"""
    
    def test_load_plugins_with_valid_config(self):
        """Test loading plugins with a valid configuration."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=self.sample_config)):
                with patch('yaml.safe_load') as mock_yaml:
                    mock_yaml.return_value = {
                        'active_plugins': ['color_mood_mapper', 'bug_buster']
                    }
                    
                    with patch('importlib.import_module') as mock_import:
                        # Mock successful plugin imports
                        mock_plugin1 = MagicMock()
                        mock_plugin1.__name__ = 'prompts.color_mood_mapper'
                        mock_plugin2 = MagicMock()
                        mock_plugin2.__name__ = 'prompts.bug_buster'
                        
                        mock_import.side_effect = [mock_plugin1, mock_plugin2]
                        
                        plugins = load_plugins('test_config.yaml')
                        
                        # Verify results
                        self.assertEqual(len(plugins), 2)
                        self.assertIn('color_mood_mapper', plugins)
                        self.assertIn('bug_buster', plugins)
                        self.assertEqual(plugins['color_mood_mapper'], mock_plugin1)
                        self.assertEqual(plugins['bug_buster'], mock_plugin2)
                        
                        # Verify import calls
                        mock_import.assert_any_call('prompts.color_mood_mapper')
                        mock_import.assert_any_call('prompts.bug_buster')
    
    def test_load_plugins_with_empty_list(self):
        """Test loading plugins when active_plugins is empty."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=self.empty_config)):
                with patch('yaml.safe_load') as mock_yaml:
                    mock_yaml.return_value = {'active_plugins': []}
                    
                    plugins = load_plugins('test_config.yaml')
                    
                    self.assertEqual(len(plugins), 0)
    
    def test_load_plugins_with_missing_config(self):
        """Test loading plugins when config file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            plugins = load_plugins('nonexistent_config.yaml')
            
            self.assertEqual(len(plugins), 0)
    
    def test_load_plugins_with_import_errors(self):
        """Test loading plugins when some plugins fail to import."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=self.sample_config)):
                with patch('yaml.safe_load') as mock_yaml:
                    mock_yaml.return_value = {
                        'active_plugins': ['color_mood_mapper', 'nonexistent_plugin']
                    }
                    
                    with patch('importlib.import_module') as mock_import:
                        # First plugin loads successfully, second fails
                        mock_plugin = MagicMock()
                        mock_plugin.__name__ = 'prompts.color_mood_mapper'
                        
                        mock_import.side_effect = [
                            mock_plugin,  # color_mood_mapper succeeds
                            ImportError("No module named 'prompts.nonexistent_plugin'")  # nonexistent_plugin fails
                        ]
                        
                        plugins = load_plugins('test_config.yaml')
                        
                        # Should only have the successful plugin
                        self.assertEqual(len(plugins), 1)
                        self.assertIn('color_mood_mapper', plugins)
                        self.assertNotIn('nonexistent_plugin', plugins)
    
    def test_get_plugin_info(self):
        """Test extracting information from a plugin module."""
        # Create a mock plugin module
        mock_plugin = MagicMock()
        mock_plugin.__name__ = 'prompts.color_mood_mapper'
        mock_plugin.__version__ = '1.0.0'
        mock_plugin.__doc__ = 'A plugin for mapping colors to moods'
        
        # Add some functions to the mock
        mock_plugin.map_color = MagicMock()
        mock_plugin.get_mood = MagicMock()
        mock_plugin._private_function = MagicMock()  # Should be ignored
        
        info = get_plugin_info(mock_plugin)
        
        self.assertEqual(info['name'], 'prompts.color_mood_mapper')
        self.assertEqual(info['version'], '1.0.0')
        self.assertEqual(info['description'], 'A plugin for mapping colors to moods')
        self.assertIn('map_color', info['functions'])
        self.assertIn('get_mood', info['functions'])
        self.assertNotIn('_private_function', info['functions'])
    
    def test_validate_plugin(self):
        """Test plugin validation."""
        # Valid plugin with functions
        valid_plugin = MagicMock()
        valid_plugin.some_function = MagicMock()
        
        self.assertTrue(validate_plugin(valid_plugin))
        
        # Invalid plugin without functions - create a simple object
        class InvalidPlugin:
            pass
        
        invalid_plugin = InvalidPlugin()
        
        self.assertFalse(validate_plugin(invalid_plugin))
    
    def test_load_plugins_with_malformed_yaml(self):
        """Test loading plugins with malformed YAML configuration."""
        malformed_config = """
active_plugins:
  - color_mood_mapper
  - bug_buster
  - [invalid, yaml, syntax
"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=malformed_config)):
                with patch('yaml.safe_load') as mock_yaml:
                    mock_yaml.side_effect = Exception("YAML parsing error")
                    
                    with self.assertRaises(Exception):
                        load_plugins('test_config.yaml')


class TestPluginLoaderIntegration(unittest.TestCase):
    """Integration tests for the plugin loader."""
    
    def setUp(self):
        """Set up temporary directory for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create prompts directory
        os.makedirs('prompts', exist_ok=True)
        
        # Create __init__.py for prompts package
        with open('prompts/__init__.py', 'w') as f:
            f.write('# Prompts package\n')
    
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_plugins_with_real_file(self):
        """Test loading plugins with a real configuration file."""
        # Create a real config file
        config_content = """
active_plugins:
  - color_mood_mapper
"""
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        # Create a real plugin file
        plugin_content = '''
"""
Color Mood Mapper Plugin

A simple plugin for mapping colors to moods.
"""

__version__ = "1.0.0"

def map_color_to_mood(color):
    """Map a color to a mood."""
    color_mood_map = {
        'red': 'passionate',
        'blue': 'calm',
        'green': 'peaceful',
        'yellow': 'happy'
    }
    return color_mood_map.get(color.lower(), 'neutral')

def get_mood_intensity(mood):
    """Get the intensity level of a mood."""
    intensity_map = {
        'passionate': 'high',
        'calm': 'low',
        'peaceful': 'low',
        'happy': 'medium'
    }
    return intensity_map.get(mood, 'unknown')
'''
        
        with open('prompts/color_mood_mapper.py', 'w') as f:
            f.write(plugin_content)
        
        # Test loading
        plugins = load_plugins('config.yaml')
        
        self.assertEqual(len(plugins), 1)
        self.assertIn('color_mood_mapper', plugins)
        
        # Test plugin functionality
        plugin = plugins['color_mood_mapper']
        self.assertEqual(plugin.map_color_to_mood('red'), 'passionate')
        self.assertEqual(plugin.get_mood_intensity('calm'), 'low')


if __name__ == '__main__':
    unittest.main() 