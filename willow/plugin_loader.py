"""
Dynamic Plugin Loading System for Willow v6

This module provides functionality to dynamically load plugins based on
configuration in config.yaml. Plugins are expected to be Python modules
located in the prompts/ directory.
"""

import importlib
import logging
import yaml
import os
from typing import List, Dict, Any, Optional


def load_plugins(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load plugins dynamically based on configuration.
    
    Args:
        config_path: Path to the configuration file containing active_plugins list
        
    Returns:
        Dictionary mapping plugin names to their loaded modules
        
    Raises:
        FileNotFoundError: If config_path doesn't exist
        yaml.YAMLError: If config file is malformed
    """
    logger = logging.getLogger(__name__)
    loaded_plugins = {}
    
    try:
        # Load configuration file
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file {config_path} not found. No plugins will be loaded.")
            return loaded_plugins
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Get list of active plugins
        active_plugins = config.get('active_plugins', [])
        
        if not active_plugins:
            logger.info("No active plugins configured in config.yaml")
            return loaded_plugins
            
        logger.info(f"Attempting to load {len(active_plugins)} plugins: {active_plugins}")
        
        # Load each plugin
        for plugin_name in active_plugins:
            try:
                # Attempt to import from prompts directory
                module_path = f"prompts.{plugin_name}"
                plugin_module = importlib.import_module(module_path)
                loaded_plugins[plugin_name] = plugin_module
                logger.info(f"Successfully loaded plugin: {plugin_name}")
                
            except ImportError as e:
                logger.warning(f"Failed to load plugin '{plugin_name}': {e}")
            except Exception as e:
                logger.warning(f"Unexpected error loading plugin '{plugin_name}': {e}")
                
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file {config_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in load_plugins: {e}")
        raise
        
    logger.info(f"Plugin loading complete. Loaded {len(loaded_plugins)} plugins successfully.")
    return loaded_plugins


def get_plugin_info(plugin_module: Any) -> Dict[str, Any]:
    """
    Extract basic information about a loaded plugin.
    
    Args:
        plugin_module: The loaded plugin module
        
    Returns:
        Dictionary containing plugin information
    """
    info = {
        'name': getattr(plugin_module, '__name__', 'unknown'),
        'version': getattr(plugin_module, '__version__', 'unknown'),
        'description': getattr(plugin_module, '__doc__', 'No description available'),
        'functions': []
    }
    
    # Get list of callable functions (excluding built-ins and private methods)
    for attr_name in dir(plugin_module):
        if not attr_name.startswith('_'):
            attr = getattr(plugin_module, attr_name)
            if callable(attr):
                info['functions'].append(attr_name)
                
    return info


def validate_plugin(plugin_module: Any) -> bool:
    """
    Validate that a plugin module has the required interface.
    
    Args:
        plugin_module: The loaded plugin module to validate
        
    Returns:
        True if plugin is valid, False otherwise
    """
    # Basic validation - check if module has any callable functions
    has_functions = any(
        callable(getattr(plugin_module, attr, None)) 
        for attr in dir(plugin_module) 
        if not attr.startswith('_')
    )
    
    return has_functions 