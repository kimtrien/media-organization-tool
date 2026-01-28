"""
File Copier Module

Handles copying files with duplicate detection and date-based organization.
"""

import os
import shutil
import logging
from pathlib import Path
from scanner import scan_folder
from exif_reader import get_image_date

logger = logging.getLogger(__name__)


def copy_image(source_path, dest_base, date):
    """
    Copy image to destination with date-based structure.
    
    Args:
        source_path: Source file path
        dest_base: Destination base directory
        date: datetime object for organizing
        
    Returns:
        dict with keys:
            - 'success': bool
            - 'dest_path': destination path (if copied or duplicate)
            - 'is_duplicate': bool
            - 'error': error message (if failed)
    """
    try:
        # Build destination path: {dest_base}/{YYYY}/{MM}/{DD}/{filename}
        filename = os.path.basename(source_path)
        year = f"{date.year:04d}"
        month = f"{date.month:02d}"
        day = f"{date.day:02d}"
        
        dest_dir = os.path.join(dest_base, year, month, day)
        dest_path = os.path.join(dest_dir, filename)
        
        # Check if destination already exists
        if os.path.exists(dest_path):
            logger.debug(f"Duplicate found: {source_path} -> {dest_path}")
            return {
                'success': False,
                'dest_path': dest_path,
                'is_duplicate': True,
                'error': None
            }
        
        # Create destination directory if needed
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy file (preserves metadata)
        shutil.copy2(source_path, dest_path)
        logger.debug(f"Copied: {source_path} -> {dest_path}")
        
        return {
            'success': True,
            'dest_path': dest_path,
            'is_duplicate': False,
            'error': None
        }
        
    except PermissionError as e:
        logger.error(f"Permission denied copying {source_path}: {e}")
        return {
            'success': False,
            'dest_path': None,
            'is_duplicate': False,
            'error': f"Permission denied: {e}"
        }
    except Exception as e:
        logger.error(f"Error copying {source_path}: {e}")
        return {
            'success': False,
            'dest_path': None,
            'is_duplicate': False,
            'error': str(e)
        }


def process_images(source_folder, dest_folder, progress_callback=None):
    """
    Process all images from source to destination.
    
    Args:
        source_folder: Source directory to scan
        dest_folder: Destination base directory
        progress_callback: Function to call with progress updates
                          Signature: callback(current, total, status_msg)
        
    Returns:
        dict with keys:
            - 'success_count': number of files copied
            - 'duplicate_count': number of duplicates found
            - 'error_count': number of errors
            - 'duplicates': list of duplicate info dicts
            - 'errors': list of error info dicts
    """
    logger.info(f"Processing images from {source_folder} to {dest_folder}")
    
    success_count = 0
    duplicate_count = 0
    error_count = 0
    duplicates = []
    errors = []
    
    # Get all image files
    image_files = list(scan_folder(source_folder))
    total_files = len(image_files)
    
    logger.info(f"Found {total_files} images to process")
    
    if progress_callback:
        progress_callback(0, total_files, "Starting processing...")
    
    for idx, source_path in enumerate(image_files, 1):
        try:
            # Extract date from image
            date = get_image_date(source_path)
            
            if not date:
                logger.warning(f"Could not extract date from: {source_path}")
                error_count += 1
                errors.append({
                    'source': source_path,
                    'error': 'Could not extract date'
                })
                continue
            
            # Copy image
            result = copy_image(source_path, dest_folder, date)
            
            if result['success']:
                success_count += 1
            elif result['is_duplicate']:
                duplicate_count += 1
                duplicates.append({
                    'source': source_path,
                    'existing': result['dest_path']
                })
            else:
                error_count += 1
                errors.append({
                    'source': source_path,
                    'error': result['error']
                })
            
            # Update progress (batch updates every 10 files)
            if progress_callback and (idx % 10 == 0 or idx == total_files):
                status = f"Processing {idx}/{total_files}: {os.path.basename(source_path)}"
                progress_callback(idx, total_files, status)
                
        except Exception as e:
            logger.error(f"Unexpected error processing {source_path}: {e}")
            error_count += 1
            errors.append({
                'source': source_path,
                'error': str(e)
            })
    
    logger.info(f"Processing complete. Success: {success_count}, Duplicates: {duplicate_count}, Errors: {error_count}")
    
    return {
        'success_count': success_count,
        'duplicate_count': duplicate_count,
        'error_count': error_count,
        'duplicates': duplicates,
        'errors': errors
    }
