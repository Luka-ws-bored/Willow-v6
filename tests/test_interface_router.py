"""
Unit tests for the Interface Router system.

Tests the interface routing logic for launching GUI or CLI modes based on configuration.
"""

import unittest
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from willow.interface_router import (
    launch_interface, 
    _launch_gui_mode, 
    _launch_cli_mode,
    get_available_interfaces,
    validate_interface_mode
)


class TestInterfaceRouter(unittest.TestCase):
    """Test cases for the interface router system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cli_config = {
            'interface_mode': 'cli',
            'active_plugins': ['color_mood_mapper', 'bug_buster']
        }
        
        self.gui_config = {
            'interface_mode': 'gui',
            'active_plugins': ['color_mood_mapper', 'bug_buster']
        }
        
        self.invalid_config = {
            'interface_mode': 'invalid_mode',
            'active_plugins': ['color_mood_mapper']
        }
    
    def test_get_available_interfaces(self):
        """Test getting list of available interfaces."""
        interfaces = get_available_interfaces()
        
        self.assertIsInstance(interfaces, list)
        self.assertIn('gui', interfaces)
        self.assertIn('cli', interfaces)
        self.assertEqual(len(interfaces), 2)
    
    def test_validate_interface_mode(self):
        """Test interface mode validation."""
        # Test valid modes
        self.assertTrue(validate_interface_mode('gui'))
        self.assertTrue(validate_interface_mode('cli'))
        self.assertTrue(validate_interface_mode('GUI'))
        self.assertTrue(validate_interface_mode('CLI'))
        
        # Test invalid modes
        self.assertFalse(validate_interface_mode('invalid'))
        self.assertFalse(validate_interface_mode('web'))
        self.assertFalse(validate_interface_mode(''))
    
    def test_launch_interface_cli_mode(self):
        """Test launching interface in CLI mode."""
        config_yaml = """
interface_mode: cli
active_plugins:
  - color_mood_mapper
  - bug_buster
"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                with patch('yaml.safe_load', return_value=self.cli_config):
                    with patch('willow.interface_router._launch_cli_mode') as mock_cli:
                        launch_interface('test_config.yaml')
                        
                        mock_cli.assert_called_once_with(self.cli_config)
    
    def test_launch_interface_gui_mode(self):
        """Test launching interface in GUI mode."""
        config_yaml = """
interface_mode: gui
active_plugins:
  - color_mood_mapper
  - bug_buster
"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                with patch('yaml.safe_load', return_value=self.gui_config):
                    with patch('willow.interface_router._launch_gui_mode') as mock_gui:
                        launch_interface('test_config.yaml')
                        
                        mock_gui.assert_called_once_with(self.gui_config)
    
    def test_launch_interface_invalid_mode(self):
        """Test launching interface with invalid mode raises error."""
        config_yaml = """
interface_mode: invalid_mode
active_plugins:
  - color_mood_mapper
"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                with patch('yaml.safe_load', return_value=self.invalid_config):
                    with self.assertRaises(ValueError) as context:
                        launch_interface('test_config.yaml')
                    
                    self.assertIn("Invalid interface_mode", str(context.exception))
    
    def test_launch_interface_missing_config_file(self):
        """Test launching interface with missing config file raises error."""
        with patch('os.path.exists', return_value=False):
            with self.assertRaises(FileNotFoundError) as context:
                launch_interface('nonexistent_config.yaml')
            
            self.assertIn("Configuration file", str(context.exception))
    
    def test_launch_interface_default_mode(self):
        """Test launching interface with no mode specified defaults to CLI."""
        config_yaml = """
active_plugins:
  - color_mood_mapper
"""
        
        config_without_mode = {'active_plugins': ['color_mood_mapper']}
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                with patch('yaml.safe_load', return_value=config_without_mode):
                    with patch('willow.interface_router._launch_cli_mode') as mock_cli:
                        launch_interface('test_config.yaml')
                        
                        mock_cli.assert_called_once_with(config_without_mode)
    
    def test_launch_cli_mode(self):
        """Test CLI mode launch functionality."""
        with patch('willow.interface_router.load_plugins') as mock_load_plugins:
            mock_plugins = {
                'color_mood_mapper': MagicMock(__name__='prompts.color_mood_mapper'),
                'bug_buster': MagicMock(__name__='prompts.bug_buster')
            }
            mock_load_plugins.return_value = mock_plugins
            
            # Capture print output
            with patch('builtins.print') as mock_print:
                _launch_cli_mode(self.cli_config)
                
                # Verify expected print calls
                expected_calls = [
                    unittest.mock.call("🌿 Launching CLI..."),
                    unittest.mock.call("Loading plugins..."),
                    unittest.mock.call("Successfully loaded 2 plugins:"),
                    unittest.mock.call("  - color_mood_mapper: prompts.color_mood_mapper"),
                    unittest.mock.call("  - bug_buster: prompts.bug_buster"),
                    unittest.mock.call("CLI mode initialized successfully!"),
                    unittest.mock.call("Plugin loading system ready for use.")
                ]
                
                mock_print.assert_has_calls(expected_calls)
    
    def test_launch_cli_mode_no_plugins(self):
        """Test CLI mode launch with no plugins loaded."""
        with patch('willow.interface_router.load_plugins') as mock_load_plugins:
            mock_load_plugins.return_value = {}
            
            with patch('builtins.print') as mock_print:
                _launch_cli_mode(self.cli_config)
                
                # Verify "No plugins loaded" message
                mock_print.assert_any_call("No plugins loaded")
    
    def test_launch_gui_mode(self):
        """Test GUI mode launch functionality."""
        with patch('builtins.print') as mock_print:
            _launch_gui_mode(self.gui_config)
            
            # Verify expected print calls
            expected_calls = [
                unittest.mock.call("🌿 Launching GUI..."),
                unittest.mock.call("GUI mode is not yet implemented in v6.0"),
                unittest.mock.call("Please use 'cli' mode or wait for v6.1 GUI implementation")
            ]
            
            mock_print.assert_has_calls(expected_calls)


class TestInterfaceRouterIntegration(unittest.TestCase):
    """Integration tests for the interface router."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        """Clean up after tests."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_launch_interface_with_real_config_file(self):
        """Test launching interface with a real configuration file."""
        # Create a real config file
        config_content = """
interface_mode: cli
active_plugins:
  - color_mood_mapper
"""
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        # Test launching interface
        with patch('willow.interface_router._launch_cli_mode') as mock_cli:
            launch_interface('config.yaml')
            
            # Verify CLI mode was called
            mock_cli.assert_called_once()
    
    def test_launch_interface_with_real_config_file_gui_mode(self):
        """Test launching interface with GUI mode in real config file."""
        # Create a real config file with GUI mode
        config_content = """
interface_mode: gui
active_plugins:
  - color_mood_mapper
"""
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        # Test launching interface
        with patch('willow.interface_router._launch_gui_mode') as mock_gui:
            launch_interface('config.yaml')
            
            # Verify GUI mode was called
            mock_gui.assert_called_once()


class TestInterfaceRouterEdgeCases(unittest.TestCase):
    """Test edge cases for the interface router."""
    
    def test_launch_interface_case_insensitive_mode(self):
        """Test that interface mode is case insensitive."""
        config_yaml = """
interface_mode: GUI
active_plugins:
  - color_mood_mapper
"""
        
        config = {'interface_mode': 'GUI', 'active_plugins': ['color_mood_mapper']}
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=config_yaml)):
                with patch('yaml.safe_load', return_value=config):
                    with patch('willow.interface_router._launch_gui_mode') as mock_gui:
                        launch_interface('test_config.yaml')
                        
                        mock_gui.assert_called_once_with(config)
    
    def test_launch_interface_malformed_yaml(self):
        """Test handling of malformed YAML configuration."""
        malformed_config = """
interface_mode: cli
active_plugins:
  - [invalid, yaml, syntax
"""
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=malformed_config)):
                with patch('yaml.safe_load') as mock_yaml:
                    mock_yaml.side_effect = Exception("YAML parsing error")
                    
                    with self.assertRaises(Exception):
                        launch_interface('test_config.yaml')


if __name__ == '__main__':
    unittest.main() 