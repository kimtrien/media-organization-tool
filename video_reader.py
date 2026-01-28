"""
Video Metadata Reader Module

Extracts date information from video files with fallback logic:
1. Video creation_time metadata
2. Filesystem modified time (fallback)
"""

import os
import logging
import subprocess
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def validate_video(file_path):
    """
    Validate if file is a valid video that can be processed.
    
    Args:
        file_path: Path to video file
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        # Use ffprobe to check if file is valid video
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'json',
                file_path
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode != 0:
            error_msg = f"Invalid video file: {result.stderr.strip()}"
            logger.warning(f"{error_msg} - {file_path}")
            return (False, error_msg)
        
        # Parse output
        data = json.loads(result.stdout)
        streams = data.get('streams', [])
        
        if not streams:
            error_msg = "No video stream found in file"
            logger.warning(f"{error_msg} - {file_path}")
            return (False, error_msg)
        
        return (True, None)
        
    except FileNotFoundError:
        error_msg = "FFmpeg/ffprobe not installed or not in PATH"
        logger.error(error_msg)
        return (False, error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing video metadata: {e}"
        logger.warning(f"{error_msg} - {file_path}")
        return (False, error_msg)
    except Exception as e:
        error_msg = f"Error validating video: {str(e)}"
        logger.warning(f"{error_msg} - {file_path}")
        return (False, error_msg)


def get_video_date(file_path):
    """
    Extract date from video file.
    
    Args:
        file_path: Path to video file
        
    Returns:
        datetime object or None if all methods fail
    """
    # Try video metadata first
    metadata_date = _get_video_metadata_date(file_path)
    if metadata_date:
        return metadata_date
    
    # Fallback to file modified time
    return _get_file_modified_date(file_path)


def _get_video_metadata_date(file_path):
    """
    Extract date from video metadata using ffprobe.
    
    Looks for:
    - creation_time in format tags
    
    Args:
        file_path: Path to video file
        
    Returns:
        datetime object or None
    """
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format_tags=creation_time',
                '-of', 'json',
                file_path
            ],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode != 0:
            logger.debug(f"ffprobe failed for: {file_path}")
            return None
        
        data = json.loads(result.stdout)
        tags = data.get('format', {}).get('tags', {})
        
        # Try creation_time
        creation_time = tags.get('creation_time') or tags.get('Creation Time')
        if creation_time:
            return _parse_video_datetime(creation_time)
        
        logger.debug(f"No creation_time in metadata: {file_path}")
        return None
        
    except FileNotFoundError:
        logger.error("FFmpeg/ffprobe not found")
        return None
    except Exception as e:
        logger.warning(f"Error reading video metadata from {file_path}: {e}")
        return None


def _parse_video_datetime(date_str):
    """
    Parse video datetime string.
    
    Common formats:
    - ISO 8601: "2024-01-15T10:30:00.000000Z"
    - Simple: "2024-01-15 10:30:00"
    
    Args:
        date_str: datetime string from video metadata
        
    Returns:
        datetime object or None
    """
    # Common datetime formats in video metadata
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",      # ISO 8601 with microseconds
        "%Y-%m-%dT%H:%M:%SZ",          # ISO 8601 without microseconds
        "%Y-%m-%dT%H:%M:%S.%f%z",      # ISO 8601 with timezone
        "%Y-%m-%dT%H:%M:%S%z",         # ISO 8601 with timezone, no microseconds
        "%Y-%m-%d %H:%M:%S",           # Simple format
        "%Y:%m:%d %H:%M:%S",           # EXIF-like format
        "%Y-%m-%d",                    # Date only
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # Try parsing with fromisoformat (Python 3.7+)
    try:
        # Handle 'Z' suffix
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        pass
    
    logger.warning(f"Could not parse video date: {date_str}")
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
