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
import cProfile
import pstats
import io

def process_file(file_path, source_folder):
    try:
        with open(file_path, 'rb') as image_file:
            image = exif.Image(image_file)
        
        if image.has_exif and hasattr(image, 'datetime_original'):
            date_time_str = image.datetime_original
            date_time = datetime.strptime(date_time_str, "%Y:%m:%d %H:%M:%S")
        else:
            date_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        year_folder = os.path.join(source_folder, str(date_time.year))
        month_folder = os.path.join(year_folder, f"{date_time.month:02d}")
        
        os.makedirs(month_folder, exist_ok=True)
        
        filename = os.path.basename(file_path)
        destination_path = os.path.join(month_folder, filename)
        
        # Copy instead of move
        shutil.copy2(file_path, destination_path)
        
        return f"Copied {filename} to {destination_path}"
    except Exception as e:
        return f"Error processing {file_path}: {str(e)}"

def get_raw_files(source_folder):
    raw_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.dng', '.cr2')):
                raw_files.append(os.path.join(root, file))
    print(f"Found {len(raw_files)} raw files (.dng and .cr2).")
    return raw_files

def sort_photos(source_folder):
    print(f"Scanning folder: {source_folder}")
    raw_files = get_raw_files(source_folder)
    
    if not raw_files:
        print("No .dng or .cr2 files found. Exiting.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        future_to_file = {executor.submit(process_file, file, source_folder): file for file in raw_files}
        
        with tqdm(total=len(raw_files), desc="Sorting photos", unit="file") as pbar:
            for future in concurrent.futures.as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    print(result)
                except Exception as exc:
                    print(f'{file} generated an exception: {exc}')
                finally:
                    pbar.update(1)

    # Delete original files after successful copy
    for file in raw_files:
        try:
            os.remove(file)
            print(f"Deleted original file: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <source_folder>")
        sys.exit(1)
    
    source_folder = os.path.abspath(sys.argv[1])
    if not os.path.isdir(source_folder):
        print(f"Error: {source_folder} is not a valid directory")
        sys.exit(1)
    
    print(f"Starting photo sorting in: {source_folder}")
    
    # Profile the script
    pr = cProfile.Profile()
    pr.enable()
    
    sort_photos(source_folder)
    
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
    
    print("\nPhoto sorting completed.")