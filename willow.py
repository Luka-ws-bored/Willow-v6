#!/usr/bin/env python3
"""
Willow v6 - AI Automation Framework

Main entry point for the Willow AI assistant system.
Handles initialization and interface routing.
"""

import logging
import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from willow.interface_router import launch_interface


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
        
        # Launch appropriate interface based on configuration
        logger.info("Launching interface...")
        launch_interface()
        
        logger.info("Willow v6 initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to start Willow: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 