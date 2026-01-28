"""
Shared Utilities Module
"""

import logging
import os


def setup_logging(log_file='image_tool.log'):
    """
    Configure logging to file and console.
    
    Args:
        log_file: Path to log file
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def is_image_file(filename, extensions):
    """
    Check if file is a supported image type.
    
    Args:
        filename: File name or path
        extensions: Set of valid extensions (with dots)
        
    Returns:
        bool
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() in extensions


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
