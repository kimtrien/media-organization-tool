"""
Media Date Extraction Module

Extracts date information from image and video files with fallback logic:

For Images:
1. EXIF DateTimeOriginal
2. EXIF DateTimeDigitized
3. EXIF DateTime
4. Filesystem modified time (fallback)

For Videos:
1. Video creation_time metadata
2. Filesystem modified time (fallback)
"""

import os
import logging
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS

from scanner import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from video_reader import validate_video, get_video_date

logger = logging.getLogger(__name__)


def validate_image(file_path):
    """
    Validate if file is a valid image that can be opened.
    
    Args:
        file_path: Path to image file
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        with Image.open(file_path) as img:
            # Try to verify the image
            img.verify()
        return (True, None)
    except Exception as e:
        error_msg = f"Cannot identify image: {str(e)}"
        logger.warning(f"{error_msg} - {file_path}")
        return (False, error_msg)


def get_image_date(file_path):
    """
    Extract date from image file.
    
    Args:
        file_path: Path to image file
        
    Returns:
        datetime object or None if all methods fail
    """
    # Try EXIF data first
    exif_date = _get_exif_date(file_path)
    if exif_date:
        return exif_date
    
    # Fallback to file modified time
    return _get_file_modified_date(file_path)


def _get_exif_date(file_path):
    """
    Extract date from EXIF metadata.
    
    Priority:
    1. DateTimeOriginal (36867)
    2. DateTimeDigitized (36868)
    3. DateTime (306)
    
    Args:
        file_path: Path to image file
        
    Returns:
        datetime object or None
    """
    try:
        with Image.open(file_path) as img:
            # Get EXIF data
            exif_data = img._getexif()
            
            if not exif_data:
                logger.debug(f"No EXIF data found: {file_path}")
                return None
            
            # Try DateTimeOriginal (most reliable)
            date_str = exif_data.get(36867)  # DateTimeOriginal
            if date_str:
                return _parse_exif_datetime(date_str)
            
            # Try DateTimeDigitized
            date_str = exif_data.get(36868)  # DateTimeDigitized
            if date_str:
                return _parse_exif_datetime(date_str)
            
            # Try DateTime
            date_str = exif_data.get(306)  # DateTime
            if date_str:
                return _parse_exif_datetime(date_str)
            
            logger.debug(f"No date tags in EXIF: {file_path}")
            return None
            
    except AttributeError:
        # _getexif() not available (e.g., PNG files)
        logger.debug(f"No EXIF support for file type: {file_path}")
        return None
    except Exception as e:
        logger.warning(f"Error reading EXIF from {file_path}: {e}")
        return None


def _parse_exif_datetime(date_str):
    """
    Parse EXIF datetime string.
    
    EXIF format: "YYYY:MM:DD HH:MM:SS"
    
    Args:
        date_str: EXIF datetime string
        
    Returns:
        datetime object or None
    """
    try:
        # EXIF datetime format
        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        try:
            # Try alternative format without time
            return datetime.strptime(date_str, "%Y:%m:%d")
        except ValueError:
            logger.warning(f"Could not parse EXIF date: {date_str}")
            return None


def _get_file_modified_date(file_path):
    """
    Get file modified time as fallback.
    
    Args:
        file_path: Path to file
        
    Returns:
        datetime object or None
    """
    try:
        mtime = os.path.getmtime(file_path)
        return datetime.fromtimestamp(mtime)
    except Exception as e:
        logger.error(f"Could not get modified time for {file_path}: {e}")
        return None


def is_video_file(file_path):
    """
    Check if file is a video based on extension.
    
    Args:
        file_path: Path to file
        
    Returns:
        bool: True if video file, False otherwise
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower() in VIDEO_EXTENSIONS


def is_image_file(file_path):
    """
    Check if file is an image based on extension.
    
    Args:
        file_path: Path to file
        
    Returns:
        bool: True if image file, False otherwise
    """
    _, ext = os.path.splitext(file_path)
    return ext.lower() in IMAGE_EXTENSIONS


def validate_media(file_path):
    """
    Validate if file is a valid media file (image or video).
    
    Args:
        file_path: Path to media file
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if is_video_file(file_path):
        return validate_video(file_path)
    else:
        return validate_image(file_path)


def get_media_date(file_path):
    """
    Extract date from media file (image or video).
    
    Args:
        file_path: Path to media file
        
    Returns:
        datetime object or None if all methods fail
    """
    if is_video_file(file_path):
        return get_video_date(file_path)
    else:
        return get_image_date(file_path)
