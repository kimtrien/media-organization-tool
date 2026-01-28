# Image Organization Tool

A lightweight Windows GUI tool for organizing image files by their EXIF date into a structured folder hierarchy.

## Features

- **Professional Icon**: Custom high-quality application icon
- **Single Executable**: Built as a standalone `.exe` for easy portability
- **Recursive Scanning**: Scans source folder at unlimited depth
- **EXIF Date Extraction**: Extracts date from image metadata with intelligent fallback
- **Date-Based Organization**: Organizes images into `YYYY/MM/DD/filename` structure
- **Duplicate Detection**: Never overwrites existing files
- **Manual Duplicate Review**: Side-by-side image comparison with manual decision options
- **Performance Optimized**: Handles 10,000+ images smoothly
- **Responsive UI**: Background processing keeps interface responsive
- **Comprehensive Error Handling**: Continues processing even with corrupted files

## Supported Image Formats

- `.jpg` / `.jpeg`
- `.png`
- `.heic`
- `.webp`

## Date Extraction Priority

1. EXIF `DateTimeOriginal` (most reliable)
2. EXIF `DateTimeDigitized`
3. EXIF `DateTime`
4. Filesystem modified time (fallback)

## Installation

### 1. Create Virtual Environment

```powershell
# Navigate to project directory
cd g:\project\ToolScanAnh

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

If you encounter execution policy errors, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

## Usage

### Running the Tool

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the application
python main.py
```

### Workflow

1. **Select Source Folder**: Click "Browse" next to "Source Folder" and select the folder containing your images
2. **Select Destination Folder**: Click "Browse" next to "Destination Folder" and select where organized images should go
3. **Start Processing**: Click "Start Processing" button
4. **Monitor Progress**: Watch the progress bar and log for real-time updates
5. **Review Duplicates** (if any):
   - After processing, you'll be prompted to review duplicates
   - View side-by-side comparison of source vs existing files
   - Choose action for each duplicate:
     - **Skip**: Keep both files (no action)
     - **Replace**: Replace existing file with source
     - **Delete Source**: Keep existing, delete source file

### Duplicate Report

After processing, a `duplicate_report.txt` file is generated in the tool directory with the format:

```
SOURCE_FILE_PATH  -->  EXISTING_DESTINATION_FILE_PATH
```

## Project Structure

```
ToolScanAnh/
├── main.py              # Main GUI and orchestration
├── scanner.py           # Recursive file scanning
├── exif_reader.py       # EXIF date extraction
├── copier.py            # File copying with duplicate detection
├── duplicate_ui.py      # Manual duplicate review window
├── utils.py             # Shared utilities
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── venv/                # Virtual environment (created by you)
```

## Error Handling

The tool is designed to never crash:

- **Corrupted Images**: Logged and skipped, processing continues
- **Missing EXIF**: Falls back to file modified time
- **Permission Errors**: Logged and skipped
- **Disk Full**: Gracefully stops with error message

All errors are logged to:
- `image_tool.log` file
- UI log window

## Performance

Optimizations for handling large image collections:

- Generator-based scanning (low memory usage)
- Metadata-only EXIF reads (fast)
- Lazy image loading (only when previewing)
- Thumbnail generation for previews (400x400 max)
- Batch UI updates (every 10 files)
- Background threading (responsive UI)

Tested with 10,000+ images.

## Troubleshooting

### HEIC Files Not Working

If HEIC files fail to process, ensure `pillow-heif` is installed:

```powershell
pip install pillow-heif
```

### Virtual Environment Activation Issues

If `.\venv\Scripts\Activate.ps1` fails, try:

```powershell
# Check execution policy
Get-ExecutionPolicy

# Set to RemoteSigned if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### GUI Not Launching

Ensure you're using Python 3.10+ with tkinter support:

```powershell
python --version
python -m tkinter
```

## License

This tool is provided as-is for personal use.

## Support

For issues or questions, check the log files:
- `image_tool.log` - Detailed processing log
- `duplicate_report.txt` - Duplicate file report
