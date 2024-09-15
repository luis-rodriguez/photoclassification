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
import concurrent.futures
import threading
import asyncio
import curses
from collections import defaultdict
import gc

# Global variables for curses output
stdscr = None
log_window = None
progress_window = None
status_window = None
processed_files = 0
total_files = 0
current_file = ""
latest_logs = []

# Abort flag
abort_event = threading.Event()

# Batch size for processing
BATCH_SIZE = 200

def setup_curses():
    global stdscr, log_window, progress_window, status_window
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    
    height, width = stdscr.getmaxyx()
    log_window = curses.newwin(height - 4, width, 0, 0)
    progress_window = curses.newwin(2, width, height - 4, 0)
    status_window = curses.newwin(2, width, height - 2, 0)

def end_curses():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def update_display():
    global log_window, progress_window, status_window, processed_files, total_files, current_file, latest_logs
    
    log_window.clear()
    for i, log in enumerate(latest_logs[-10:]):  # Show last 10 log entries
        log_window.addstr(i, 0, log[:log_window.getmaxyx()[1]-1])
    log_window.refresh()
    
    progress_window.clear()
    progress_percent = (processed_files / total_files) * 100 if total_files > 0 else 0
    progress_window.addstr(0, 0, f"Progress: [{processed_files}/{total_files}] {progress_percent:.2f}%")
    progress_window.addstr(1, 0, f"Current file: {current_file[:progress_window.getmaxyx()[1]-1]}", curses.color_pair(1))
    progress_window.refresh()
    
    status_window.clear()
    status_window.addstr(0, 0, "Press 'q' to quit")
    status_window.refresh()

def log_message(message):
    global latest_logs
    latest_logs.append(message)
    if len(latest_logs) > 100:  # Keep only last 100 log entries
        latest_logs.pop(0)
    update_display()

def analyze_file(file_path, source_folder, update_names):
    global processed_files, current_file
    if abort_event.is_set():
        return None
    thread_id = threading.get_ident()
    current_file = file_path
    log_message(f"Thread {thread_id}: Analyzing {file_path}")
    try:
        with open(file_path, 'rb') as image_file:
            image = exif.Image(image_file)
        
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
        
        filename = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(filename)
        
        if update_names:
            new_filename = f"{date_time.strftime('%Y-%m-%d-%H%M%S')}_{file_name}{file_extension}"
        else:
            new_filename = filename
        
        destination_path = os.path.join(month_folder, new_filename)
        
        processed_files += 1
        update_display()
        return (file_path, destination_path)
    except Exception as e:
        log_message(f"Thread {thread_id}: Error analyzing {file_path}: {str(e)}")
        return None

def get_image_files(source_folder):
    image_files = []
    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if file.lower().endswith(('.dng', '.cr2', '.jpg', '.jpeg')):
                image_files.append(os.path.join(root, file))
    log_message(f"Found {len(image_files)} image files (.dng, .cr2, .jpg, .jpeg).")
    return image_files

async def analyze_photos(source_folder, update_names):
    global total_files
    log_message(f"Scanning folder: {source_folder}")
    image_files = get_image_files(source_folder)
    total_files = len(image_files)
    
    if not image_files:
        log_message("No image files found. Exiting.")
        return []

    all_results = []
    for i in range(0, len(image_files), BATCH_SIZE):
        batch = image_files[i:i+BATCH_SIZE]
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, os.cpu_count() + 4)) as executor:
            futures = [loop.run_in_executor(executor, analyze_file, file, source_folder, update_names) for file in batch]
            results = []
            for future in asyncio.as_completed(futures):
                if abort_event.is_set():
                    break
                try:
                    result = await future
                    if result:
                        results.append(result)
                except Exception as exc:
                    log_message(f'Error: {exc}')
            all_results.extend(results)
        
        # Perform garbage collection after each batch
        gc.collect()
        
        if abort_event.is_set():
            break
    
    return all_results

def execute_file_operations(operations):
    log_message("Executing file operations...")
    for source, destination in operations:
        if abort_event.is_set():
            break
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            log_message(f"Copied {source} to {destination}")
        except Exception as e:
            log_message(f"Error copying {source}: {str(e)}")

    if not abort_event.is_set():
        log_message("Deleting original files...")
        for source, _ in operations:
            if abort_event.is_set():
                break
            try:
                os.remove(source)
                log_message(f"Deleted original file: {source}")
            except Exception as e:
                log_message(f"Error deleting {source}: {str(e)}")

def input_thread(stdscr):
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            abort_event.set()
            break

async def main(source_folder, update_names):
    try:
        setup_curses()
        log_message(f"Starting photo analysis in: {source_folder}")
        log_message(f"Update names: {'Yes' if update_names else 'No'}")
        log_message(f"Number of CPU cores: {os.cpu_count()}")
        
        # Start input thread
        input_thread_handle = threading.Thread(target=input_thread, args=(stdscr,))
        input_thread_handle.start()
        
        operations = await analyze_photos(source_folder, update_names)
        
        if abort_event.is_set():
            log_message("Operation aborted by user.")
        else:
            log_message("\nAnalysis completed. Starting file operations...")
            execute_file_operations(operations)
            log_message("\nPhoto sorting completed.")
        
        log_message("Press any key to exit...")
        stdscr.getch()
    except Exception as e:
        log_message(f"An error occurred: {str(e)}")
    finally:
        end_curses()

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script_name.py <source_folder> [updatenames]")
        sys.exit(1)
    
    source_folder = os.path.abspath(sys.argv[1])
    if not os.path.isdir(source_folder):
        print(f"Error: {source_folder} is not a valid directory")
        sys.exit(1)
    
    update_names = len(sys.argv) == 3 and sys.argv[2].lower() == 'updatenames'
    
    asyncio.run(main(source_folder, update_names))