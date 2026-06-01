"""
HPE Morpheus Appliance Inventory - Central Logging Module
Provides centralized logging for all modules
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Create log filename with timestamp
log_filename = log_dir / f"morpheus_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logger
logger = logging.getLogger('MorpheusInventory')
logger.setLevel(logging.DEBUG)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

simple_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler - logs everything (DEBUG and above)
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# Console handler - logs INFO and above
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Convenience functions
def info(msg):
    """Log an info message"""
    logger.info(msg)

def error(msg, exc_info=False):
    """Log an error message"""
    logger.error(msg, exc_info=exc_info)

def warning(msg):
    """Log a warning message"""
    logger.warning(msg)

def debug(msg):
    """Log a debug message"""
    logger.debug(msg)

def exception(msg):
    """Log an exception with traceback"""
    logger.exception(msg)

# Log initialization
logger.info(f"Logging initialized - Log file: {log_filename}")
