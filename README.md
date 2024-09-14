# Photo Date Classifier

This Python script organizes digital raw photo files (DNG and CR2) into a folder structure based on their creation date. It uses multi-threading for improved performance, making it efficient for large collections of photos.

## Features

- Recursively scans a source folder for DNG and CR2 files
- Reads EXIF data to determine the creation date of each photo
- Falls back to file modification time if EXIF data is unavailable
- Organizes photos into a Year/Month folder structure
- Uses multi-threading for faster processing
- Provides a progress bar to track the sorting process
- Option to update filenames with date and time information

## Requirements

- Python 3.x
- exif library
- tqdm library

## Installation

1. Clone this repository or download the script.
2. Install the required libraries:

```bash
pip install exif tqdm
pip install exif exif
```

## Usage
Run the script from the command line, providing the path to the folder containing your photos as an argument:

```bash
date-classifier.py /path/to/your/photo/folder [updatenames]
```

Replace /path/to/your/photo/folder with the actual path to the folder containing your photos.
The optional ´updatenames´ parameter, when included, will update the filenames to include the date and time information.
How It Works

- The script scans the provided folder and all its subfolders for DNG and CR2 files.
- For each file, it attempts to read the creation date from the EXIF metadata.
- If EXIF data is unavailable, it uses the file's modification time.
- It creates a Year/Month folder structure in the source folder.
- Each photo is copied to its corresponding Year/Month folder.
- If the updatenames option is used, the filename is updated to the format: {yyyy-mm-dd-hhmmss}_{originalFileName}.{extension}
- After successful copying, the original files are deleted from the source location.
- The script uses multi-threading to process multiple files concurrently, significantly improving performance for large collections.

## Notes

This script will modify the file structure in the source folder. It's recommended to backup your files before running this script.
The script preserves the original filenames of the photos unless the updatenames option is used.
While designed for DNG and CR2 files, you can easily modify the script to include other raw formats by editing the file extension check in the get_raw_files function.
The script now copies files to the new location and then deletes the originals, which can be faster in some situations, especially when moving files across different drives.

## Contributing
Feel free to fork this repository and submit pull requests with any enhancements.

## License
MIT License