"""
Test script to create sample images with EXIF data for testing.
"""

from PIL import Image
from PIL.ExifTags import TAGS
import piexif
from datetime import datetime, timedelta
import os

def create_test_images():
    """Create test images with various EXIF dates."""
    
    # Create test_images directory
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    print(f"Creating test images in {test_dir}/")
    
    # Test dates
    test_dates = [
        ("2024-01-15 10:30:00", "image_2024_01_15.jpg"),
        ("2024-02-20 14:45:00", "image_2024_02_20.jpg"),
        ("2024-03-10 09:15:00", "image_2024_03_10.jpg"),
        ("2023-12-25 16:00:00", "image_2023_12_25.jpg"),
        ("2025-06-01 12:00:00", "image_2025_06_01.jpg"),
    ]
    
    for date_str, filename in test_dates:
        # Create a simple colored image
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        
        # Parse date
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        
        # Create EXIF data
        exif_dict = {
            "0th": {},
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: dt.strftime("%Y:%m:%d %H:%M:%S"),
                piexif.ExifIFD.DateTimeDigitized: dt.strftime("%Y:%m:%d %H:%M:%S"),
            }
        }
        
        exif_bytes = piexif.dump(exif_dict)
        
        # Save with EXIF
        filepath = os.path.join(test_dir, filename)
        img.save(filepath, "JPEG", exif=exif_bytes)
        print(f"  Created: {filename} with date {date_str}")
    
    # Create image without EXIF (will use file modified time)
    img_no_exif = Image.new('RGB', (800, 600), color=(200, 100, 50))
    no_exif_path = os.path.join(test_dir, "image_no_exif.jpg")
    img_no_exif.save(no_exif_path, "JPEG")
    print(f"  Created: image_no_exif.jpg (no EXIF data)")
    
    # Create PNG (no EXIF support)
    img_png = Image.new('RGB', (800, 600), color=(50, 150, 200))
    png_path = os.path.join(test_dir, "image_test.png")
    img_png.save(png_path, "PNG")
    print(f"  Created: image_test.png (PNG format)")
    
    print(f"\nTest images created successfully!")
    print(f"Use '{test_dir}' as your source folder for testing.")

if __name__ == '__main__':
    create_test_images()
