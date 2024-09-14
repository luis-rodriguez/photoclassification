"""
Photo Sorting Script

This script organizes Digital Negative (DNG) photo files into a folder structure based on their creation date.

Functionality:
1. Accepts a source folder path as a command-line argument.
2. Recursively scans the source folder and all its subfolders for .dng files.
3. For each file, it attempts to read the creation date from EXIF metadata.
4. If EXIF data is unavailable, it falls back to using the file's modification time.
5. Creates a folder structure: YYYY/MM (Year/Month) in the source folder.
6. Moves each photo into its corresponding year and month folder.
7. Displays a progress bar during the sorting process.

Usage:
python date-classifier.py <source_folder>

Requirements:
- Python 3.x
- exif library (install with: pip install exif)
- tqdm library (install with: pip install tqdm)

Note: This script will modify the file structure in the source folder. 
It's recommended to backup your files before running this script.
"""
import os
import shutil
import sys
from datetime import datetime
import exif
from tqdm import tqdm

def get_raw_files(source_folder):
    raw_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.dng', '.cr2')):
                raw_files.append(os.path.join(root, file))
    print(f"Found {len(raw_files)} raw files (.dng and .cr2).")
    if len(raw_files) == 0:
        print("Contents of the directory:")
        for item in os.listdir(source_folder):
            print(item)
    return raw_files

def sort_photos(source_folder):
    print(f"Scanning folder: {source_folder}")
    raw_files = get_raw_files(source_folder)
    
    if not raw_files:
        print("No .dng or .cr2 files found. Exiting.")
        return

    with tqdm(total=len(raw_files), desc="Sorting photos", unit="file") as pbar:
        for file_path in raw_files:
            try:
                print(f"\nProcessing: {file_path}")
                with open(file_path, 'rb') as image_file:
                    image = exif.Image(image_file)
                
                if image.has_exif and hasattr(image, 'datetime_original'):
                    date_time_str = image.datetime_original
                    date_time = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
                    print(f"EXIF date found: {date_time}")
                else:
                    date_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    print(f"Using file modification time: {date_time}")
                
                year_folder = os.path.join(source_folder, str(date_time.year))
                month_folder = os.path.join(year_folder, f"{date_time.month:02d}")
                
                if not os.path.exists(month_folder):
                    os.makedirs(month_folder)
                    print(f"Created folder: {month_folder}")
                
                filename = os.path.basename(file_path)
                destination_path = os.path.join(month_folder, filename)
                shutil.move(file_path, destination_path)
                print(f"Moved file to: {destination_path}")
                
                pbar.update(1)
            
            except Exception as e:
                print(f"\nError processing {file_path}: {str(e)}")
                pbar.update(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <source_folder>")
        sys.exit(1)
    
    source_folder = os.path.abspath(sys.argv[1])
    if not os.path.isdir(source_folder):
        print(f"Error: {source_folder} is not a valid directory")
        sys.exit(1)
    
    print(f"Starting photo sorting in: {source_folder}")
    sort_photos(source_folder)
    print("\nPhoto sorting completed.")