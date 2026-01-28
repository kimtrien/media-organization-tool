"""
Media Scanner Module

Recursively scans directories for image and video files.
"""

import os
import logging

logger = logging.getLogger(__name__)

# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.webp', '.gif', '.bmp', '.tiff', '.tif'}

# Supported video extensions
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp'}

# Combined supported extensions
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS


def scan_folder(folder_path, extensions=None):
    """
    Recursively scan folder for image files.
    
    Args:
        folder_path: Root folder to scan
        extensions: Set of extensions to include (default: SUPPORTED_EXTENSIONS)
        
    Yields:
        Full path to each image file found
    """
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS
    
    # Normalize extensions to lowercase
    extensions = {ext.lower() for ext in extensions}
    
    logger.info(f"Starting scan of: {folder_path}")
    count = 0
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                # Check extension (case-insensitive)
                _, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    full_path = os.path.join(root, filename)
                    count += 1
                    yield full_path
    except PermissionError as e:
        logger.error(f"Permission denied accessing: {e}")
    except Exception as e:
        logger.error(f"Error scanning folder: {e}")
    
    logger.info(f"Scan complete. Found {count} image files.")


def count_images(folder_path, extensions=None):
    """
    Count total images in folder (for progress tracking).
    
    Args:
        folder_path: Root folder to scan
        extensions: Set of extensions to include
        
    Returns:
        Total count of image files
    """
    return sum(1 for _ in scan_folder(folder_path, extensions))
