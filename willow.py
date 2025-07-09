#!/usr/bin/env python3
"""
Willow v6 - AI Automation Framework

Main entry point for the Willow AI assistant system.
Handles initialization and interface routing.
"""

import logging
import sys
import os
import yaml
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from willow.interface_router import launch_interface
from willow.memory import MemoryManager
from willow.subconscious import Subconscious
from willow import validate_environment


def setup_logging():
    """Configure logging for the Willow application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('willow.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for Willow v6."""
    logger = logging.getLogger(__name__)
    
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting Willow v6 - AI Automation Framework")
        
        # Validate environment variables
        validate_environment()
        
        # Load configuration
        config_path = "config.yaml"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file {config_path} not found")
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize memory manager
        memory_config = config.get('memory', {})
        memory_enabled = memory_config.get('enabled', True)
        memory_path = memory_config.get('path', 'memory.json')
        
        memory = None
        if memory_enabled:
            memory = MemoryManager(memory_path)
            logger.info(f"Memory system initialized with file: {memory_path}")
        
        # Initialize Subconscious agent
        subconscious = Subconscious(memory, config['subconscious']['dream_interval'])
        if config['subconscious']['enabled']:
            subconscious.start()
        
        # Launch appropriate interface based on configuration
        logger.info("Launching interface...")
        launch_interface(config, memory)
        
        logger.info("Willow v6 initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to start Willow: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 