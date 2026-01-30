import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from scanner import scan_folder
from exif_reader import get_media_date, validate_media, is_video_file
from utils import are_files_identical

logger = logging.getLogger(__name__)


def copy_file(source_path, dest_base, date, move_files=False, check_binary=False):
    """
    Copy or move media file to destination with date-based structure.
    
    Args:
        source_path: Source file path
        dest_base: Destination base directory
        date: datetime object for organizing
        move_files: Whether to move instead of copy
        check_binary: Whether to check binary equality for duplicates
        
    Returns:
        dict with keys:
            - 'success': bool
            - 'dest_path': destination path (if copied or duplicate)
            - 'is_duplicate': bool
            - 'is_identical': bool (if binary checked and matched)
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
            is_identical = False
            if check_binary:
                is_identical = are_files_identical(source_path, dest_path)
                logger.debug(f"Duplicate found (Identical: {is_identical}): {source_path} -> {dest_path}")
            else:
                logger.debug(f"Duplicate found: {source_path} -> {dest_path}")
                
            return {
                'success': False,
                'dest_path': dest_path,
                'is_duplicate': True,
                'is_identical': is_identical,
                'error': None
            }
        
        # Create destination directory if needed
        os.makedirs(dest_dir, exist_ok=True)
        
        if move_files:
            # Move file
            shutil.move(source_path, dest_path)
            logger.debug(f"Moved: {source_path} -> {dest_path}")
        else:
            # Copy file (preserves metadata)
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Copied: {source_path} -> {dest_path}")
        
        return {
            'success': True,
            'dest_path': dest_path,
            'is_duplicate': False,
            'is_identical': False,
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


def _write_invalid_images_log(invalid_files, log_dir):
    """
    Write invalid images/files to a separate log file.
    
    Args:
        invalid_files: List of invalid file dicts with 'source' and 'error' keys
        log_dir: Directory to save the log file
        
    Returns:
        str: Path to the created log file
    """
    try:
        # Create logs directory if it doesn't exist (should be passed in)
        os.makedirs(log_dir, exist_ok=True)
        
        # Filename inside the session folder
        log_filename = "invalid_files.log"
        log_path = os.path.join(log_dir, log_filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Invalid Images Log - Generated {datetime.now()}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Total invalid images: {len(invalid_images)}\n\n")
            
            for item in invalid_images:
                f.write(f"File: {item['source']}\n")
                f.write(f"Error: {item['error']}\n")
                f.write(f"{'-'*80}\n")
        
        logger.info(f"Invalid images log saved to: {log_path}")
        return log_path
        
    except Exception as e:
        logger.error(f"Error writing invalid images log: {e}")
        return None


def _write_success_log(success_files, log_dir):
    """
    Write successfully copied files to a separate log file.
    
    Args:
        success_files: List of success dicts with 'source' and 'destination' keys
        log_dir: Directory to save the log file
        
    Returns:
        str: Path to the created log file
    """
    try:
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Filename inside session folder
        log_filename = "success_report.txt"
        log_path = os.path.join(log_dir, log_filename)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Success Report - Generated {datetime.now()}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Total files copied successfully: {len(success_files)}\n\n")
            
            for item in success_files:
                f.write(f"{item['source']}  -->  {item['destination']}\n")
        
        logger.info(f"Success report saved to: {log_path}")
        return log_path
        
    except Exception as e:
        logger.error(f"Error writing success report: {e}")
        return None




def process_media(source_folder, dest_folder, move_files=False, delete_duplicates=False, log_dir=None, progress_callback=None):
    """
    Process all media files (images and videos) from source to destination.
    
    Args:
        source_folder: Source directory to scan
        dest_folder: Destination base directory
        move_files: Whether to move instead of copy
        delete_duplicates: Whether to check and flag duplicates for deletion (strict check)
        log_dir: Directory to save logs/reports
        progress_callback: Function to call with progress updates
                          Signature: callback(current, total, status_msg)
        
    Returns:
        dict with keys:
            - 'success_count': number of files processed
            - 'image_count': number of images processed
            - 'video_count': number of videos processed
            - 'duplicate_count': number of duplicates found
            - 'error_count': number of errors
            - 'invalid_count': number of invalid files (cannot identify)
            - 'duplicates': list of duplicate info dicts
            - 'errors': list of error info dicts
            - 'invalid_files': list of invalid file info dicts
            - 'success_files': list of successfully processed files
            - 'invalid_log_path': path to invalid files log
            - 'success_log_path': path to success report
    """
    logger.info(f"Processing media from {source_folder} to {dest_folder} (Move: {move_files}, Delete Dups: {delete_duplicates})")
    
    success_count = 0
    image_count = 0
    video_count = 0
    duplicate_count = 0
    error_count = 0
    invalid_count = 0
    duplicates = []
    errors = []
    invalid_files = []
    success_files = []
    
    # Get all media files
    media_files = list(scan_folder(source_folder))
    total_files = len(media_files)
    
    logger.info(f"Found {total_files} media files to process")
    
    if progress_callback:
        progress_callback(0, total_files, "Starting processing...")
    
    for idx, source_path in enumerate(media_files, 1):
        try:
            # Validate media file first
            is_valid, error_msg = validate_media(source_path)
            
            if not is_valid:
                logger.warning(f"Invalid file, skipping: {source_path}")
                if progress_callback:
                    progress_callback(idx, total_files, f"Skipped (invalid): {os.path.basename(source_path)}")
                invalid_count += 1
                invalid_files.append({
                    'source': source_path,
                    'error': error_msg
                })
                continue
            
            # Extract date from media
            date = get_media_date(source_path)
            
            if not date:
                logger.warning(f"Could not extract date from: {source_path}")
                if progress_callback:
                    progress_callback(idx, total_files, f"Skipped (no date): {os.path.basename(source_path)}")
                error_count += 1
                errors.append({
                    'source': source_path,
                    'error': 'Could not extract date'
                })
                continue
            
            # Process file (copy or move)
            result = copy_file(
                source_path, 
                dest_folder, 
                date, 
                move_files=move_files,
                check_binary=delete_duplicates
            )
            
            if result['success']:
                success_count += 1
                # Track image vs video count
                if is_video_file(source_path):
                    video_count += 1
                else:
                    image_count += 1
                success_files.append({
                    'source': source_path,
                    'destination': result['dest_path']
                })
            elif result['is_duplicate']:
                duplicate_count += 1
                if progress_callback:
                    progress_callback(idx, total_files, f"Duplicate found: {os.path.basename(source_path)}")
                duplicates.append({
                    'source': source_path,
                    'existing': result['dest_path'],
                    'is_identical': result.get('is_identical', False)
                })
            else:
                error_count += 1
                if progress_callback:
                    progress_callback(idx, total_files, f"Error: {result['error']} - {os.path.basename(source_path)}")
                errors.append({
                    'source': source_path,
                    'error': result['error']
                })
            
            # Update progress (batch updates every 10 files for performance, but show filename)
            if progress_callback and (idx % 10 == 0 or idx == total_files):
                status = f"Processed {idx}/{total_files} files..."
                progress_callback(idx, total_files, status)
                
        except Exception as e:
            logger.error(f"Unexpected error processing {source_path}: {e}")
            error_count += 1
            errors.append({
                'source': source_path,
                'error': str(e)
            })
    
    # Write invalid files log if any
    invalid_log_path = None
    if invalid_files and log_dir:
        invalid_log_path = _write_invalid_images_log(invalid_files, log_dir)
    
    # Write success log if any
    success_log_path = None
    if success_files and log_dir:
        success_log_path = _write_success_log(success_files, log_dir)
    
    logger.info(f"Processing complete. Success: {success_count} (Images: {image_count}, Videos: {video_count}), Duplicates: {duplicate_count}, Invalid: {invalid_count}, Errors: {error_count}")
    
    return {
        'success_count': success_count,
        'image_count': image_count,
        'video_count': video_count,
        'duplicate_count': duplicate_count,
        'error_count': error_count,
        'invalid_count': invalid_count,
        'duplicates': duplicates,
        'errors': errors,
        'invalid_files': invalid_files,
        'success_files': success_files,
        'invalid_log_path': invalid_log_path,
        'success_log_path': success_log_path
    }

