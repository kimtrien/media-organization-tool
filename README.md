# Media Organization Tool

A lightweight Windows GUI tool for organizing image and video files by their EXIF/Metadata date into a structured folder hierarchy.

## Features

- **Video & HEIC Support**: Handles images, videos (MP4, MOV, etc.), and HEIC files seamlessly.
- **Smart Duplicate Management**:
  - **Binary Match**: Optional strict bit-for-bit comparison to identify identical files.
  - **Auto-Marking**: Perfectly identical files are automatically pre-selected for deletion to save you time.
  - **Batch Deletion**: Review all duplicates first, then delete all marked files in one click.
- **Safe Operation**:
  - **Recycle Bin Integration**: Deleted files are moved to the Windows Recycle Bin, not permanently erased.
  - **Non-Destructive**: Never overwrites existing files; duplicates are always flagged for your review.
- **Improved UX**:
  - **Keyboard Shortcuts**: Use `Left`/`Right` to navigate, and `Space` or `X` to mark for deletion.
  - **Asynchronous Loading**: Image previews load in the background, keeping the UI smooth and lag-free.
  - **Professional Look**: Custom high-quality icon and clean layout.
- **Portability**: Standalone `.exe` included for easy use without installing Python.
- **Session-Based Logging**: Stores logs, success reports, and invalid file lists in timestamped folders.
- **Smart History**: Remembers your recently used destination folders.
- **Reliable**: Handles 10,000+ files with comprehensive error handling and background threading.

## Supported Formats

### Images
- `.jpg` / `.jpeg`
- `.png`
- `.heic` (requires `pillow-heif`)
- `.webp`
- `.gif`
- `.bmp`
- `.tiff`

### Videos
- `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`, `.flv`, `.webm`, `.m4v`, `.3gp`

## Date Extraction Priority

### Images
1. EXIF `DateTimeOriginal`
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. Filesystem modified time (fallback)

### Videos
1. Video `creation_time` metadata
2. Filesystem modified time (fallback)

## Installation (for Developers)

### 1. Requirements
- **Python 3.10+**
- **FFmpeg**: Required for video metadata extraction (must be in system PATH)

### 2. Setup
```powershell
# Create & Activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install Dependencies
pip install -r requirements.txt
```

## Usage

1. **Select Folders**: Choose your Source (where photos are) and Destination (where they should go).
2. **Options**: 
   - Check "Move files" to delete originals after copying.
   - Check "Check for Duplicate Content" to use Binary Match for safer identification.
3. **Start**: Click "Start Processing".
4. **Duplicate Review**:
   - Navigate using buttons or `←` / `→` keys.
   - Mark files for deletion using checkbox or `Space`/`X` keys.
   - Identical files are marked **[DEL]** automatically.
   - Click **"DELETE MARKED FILES NOW"** to send them to the Recycle Bin.

## Project Structure
- `main.py`: Main GUI and orchestration.
- `copier.py`: Core logic for sorting and binary comparison.
- `duplicate_ui.py`: Enhanced review interface with async loading.
- `exif_reader.py`: Metadata extraction for images and videos.
- `scanner.py`: Recursive file discovery.

## Error Handling
All logs are saved in `logs/<session_timestamp>/`:
- `session.log`: Full technical details.
- `success_report.txt`: List of organized files.
- `invalid_files.log`: Files skipped due to corruption or missing data.
- `duplicate_report.txt`: Summary of all duplicate pairs found.

## Performance
- Non-blocking I/O for smooth UI.
- Lazy thumbnail generation for previews.
- Generator-based scanning for minimal memory footprint.

## License
Provided as-is for personal use.
