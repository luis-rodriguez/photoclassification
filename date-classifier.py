"""
Photo Sorting Script
Usage: python date-classifier.py <source_folder>

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
import concurrent.futures
import threading
import asyncio
import aiofiles

async def process_file(file_path, source_folder, update_names):
    thread_id = threading.get_ident()
    try:
        async with aiofiles.open(file_path, 'rb') as image_file:
            image_data = await image_file.read()
            image = exif.Image(image_data)
        
        try:
            if image.has_exif and hasattr(image, 'datetime_original'):
                date_time_str = image.datetime_original
                date_time = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
            else:
                raise ValueError("No valid EXIF data")
        except (ValueError, AttributeError):
            date_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        year_folder = os.path.join(source_folder, str(date_time.year))
        month_folder = os.path.join(year_folder, f"{date_time.month:02d}")
        
        os.makedirs(month_folder, exist_ok=True)
        
        filename = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(filename)
        
        if update_names:
            new_filename = f"{date_time.strftime('%Y-%m-%d-%H%M%S')}_{file_name}{file_extension}"
        else:
            new_filename = filename
        
        destination_path = os.path.join(month_folder, new_filename)
        
        await aiofiles.os.copy(file_path, destination_path)
        
        return f"Thread {thread_id}: Copied {filename} to {destination_path}"
    except Exception as e:
        return f"Thread {thread_id}: Error processing {file_path}: {str(e)}"

def get_image_files(source_folder):
    image_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.dng', '.cr2', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
    print(f"Found {len(image_files)} image files (.dng, .cr2, .jpg, .jpeg).")
    return image_files

async def sort_photos(source_folder, update_names):
    print(f"Scanning folder: {source_folder}")
    image_files = get_image_files(source_folder)
    
    if not image_files:
        print("No image files found. Exiting.")
        return

    tasks = [process_file(file, source_folder, update_names) for file in image_files]
    
    with tqdm(total=len(image_files), desc="Sorting photos", unit="file") as pbar:
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                print(result)
            except Exception as exc:
                print(f'Error: {exc}')
            finally:
                pbar.update(1)

    # Delete original files after successful copy
    for file in image_files:
        try:
            os.remove(file)
            print(f"Deleted original file: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script_name.py <source_folder> [updatenames]")
        sys.exit(1)
    
    source_folder = os.path.abspath(sys.argv[1])
    if not os.path.isdir(source_folder):
        print(f"Error: {source_folder} is not a valid directory")
        sys.exit(1)
    
    update_names = len(sys.argv) == 3 and sys.argv[2].lower() == 'updatenames'
    
    print(f"Starting photo sorting in: {source_folder}")
    print(f"Update names: {'Yes' if update_names else 'No'}")
    
    asyncio.run(sort_photos(source_folder, update_names))
    
    print("\nPhoto sorting completed.")