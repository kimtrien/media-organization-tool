"""
Shared Utilities Module
"""

import logging
import os
from datetime import datetime


def setup_logging(log_file='image_tool.log'):
    """
    Configure logging to file and console.
    
    Args:
        log_file: Base name for log file (timestamp will be added)
    """
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    os.makedirs(logs_dir, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"image_tool_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
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


def are_files_identical(path1, path2, chunk_size=4096):
    """
    Check if two files are bit-for-bit identical.
    
    Args:
        path1: Path to first file
        path2: Path to second file
        chunk_size: Size of chunks to read/compare
        
    Returns:
        bool: True if identical, False otherwise
    """
    try:
        # Check size first (fastest)
        if os.path.getsize(path1) != os.path.getsize(path2):
            return False
            
        # Compare binary content
        with open(path1, 'rb') as f1, open(path2, 'rb') as f2:
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                
                if chunk1 != chunk2:
                    return False
                    
                if not chunk1:  # EOF
                    return True
                    
    except OSError as e:
        # If any file access error (e.g. missing, locked), assume different to be safe
        logging.getLogger(__name__).warning(f"Error comparing files: {e}")
        return False
