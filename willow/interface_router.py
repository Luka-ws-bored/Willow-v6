"""
Interface Router for Willow v6

This module handles launching the appropriate interface (GUI or CLI) based on
configuration settings. It serves as the entry point for different user interfaces.
"""

import logging
import yaml
import os
from typing import Optional
from .plugin_loader import load_plugins


def launch_interface(config_path: str = "config.yaml") -> None:
    """
    Launch the appropriate interface based on configuration.
    
    Args:
        config_path: Path to the configuration file
        
    Raises:
        ValueError: If interface_mode is invalid
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is malformed
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Load configuration
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {config_path} not found")
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Get interface mode
        interface_mode = config.get('interface_mode', 'cli').lower()
        logger.info(f"Launching interface in {interface_mode.upper()} mode")
        
        # Route to appropriate interface
        if interface_mode == 'gui':
            _launch_gui_mode(config)
        elif interface_mode == 'cli':
            _launch_cli_mode(config)
        else:
            raise ValueError(f"Invalid interface_mode: {interface_mode}. Must be 'gui' or 'cli'")
            
    except Exception as e:
        logger.error(f"Failed to launch interface: {e}")
        raise


def _launch_gui_mode(config: dict) -> None:
    """
    Launch Willow in GUI mode.
    
    Args:
        config: Configuration dictionary
        
    TODO: Implement full GUI interface
    """
    print("🌿 Launching GUI...")
    print("GUI mode is not yet implemented in v6.0")
    print("Please use 'cli' mode or wait for v6.1 GUI implementation")
    
    # TODO: Initialize GUI components
    # TODO: Load GUI framework (PyQt6/Tkinter)
    # TODO: Create main window
    # TODO: Setup event handlers
    # TODO: Start GUI event loop


def _launch_cli_mode(config: dict) -> None:
    """
    Launch Willow in CLI mode.
    
    Args:
        config: Configuration dictionary
    """
    print("🌿 Launching CLI...")
    
    try:
        # Load plugins as part of CLI initialization
        print("Loading plugins...")
        plugins = load_plugins()
        
        if plugins:
            print(f"Successfully loaded {len(plugins)} plugins:")
            for plugin_name, plugin_module in plugins.items():
                print(f"  - {plugin_name}: {plugin_module.__name__}")
        else:
            print("No plugins loaded")
        
        # TODO: Initialize CLI components
        # TODO: Setup command line interface
        # TODO: Start interactive CLI loop
        # TODO: Handle user input and routing
        
        print("CLI mode initialized successfully!")
        print("Plugin loading system ready for use.")
        
    except Exception as e:
        print(f"Error initializing CLI mode: {e}")
        raise


def get_available_interfaces() -> list:
    """
    Get list of available interface modes.
    
    Returns:
        List of available interface modes
    """
    return ['gui', 'cli']


def validate_interface_mode(mode: str) -> bool:
    """
    Validate if an interface mode is supported.
    
    Args:
        mode: Interface mode to validate
        
    Returns:
        True if mode is valid, False otherwise
    """
    return mode.lower() in get_available_interfaces() 