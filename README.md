# Photo Date Classifier

This Python script organizes digital raw photo files (DNG and CR2) into a folder structure based on their creation date. It uses multi-threading for improved performance, making it efficient for large collections of photos.

## Features

- Recursively scans a source folder for DNG and CR2 files
- Reads EXIF data to determine the creation date of each photo
- Falls back to file modification time if EXIF data is unavailable
- Organizes photos into a Year/Month folder structure
- Uses multi-threading for faster processing
- Provides a progress bar to track the sorting process

## Requirements

- Python 3.x
- exif library
- tqdm library

## Installation

1. Clone this repository or download the script.
2. Install the required libraries:

```bash
pip install exif tqdm
```

## Usage

Run the script from the command line, providing the path to the folder containing your photos as an argument:

```bash
python date-classifier.py /path/to/your/photo/folder
```

Replace `/path/to/your/photo/folder` with the actual path to the folder containing your photos.

## How It Works

1. The script scans the provided folder and all its subfolders for DNG and CR2 files.
2. For each file, it attempts to read the creation date from the EXIF metadata.
3. If EXIF data is unavailable, it uses the file's modification time.
4. It creates a Year/Month folder structure in the source folder.
5. Each photo is moved to its corresponding Year/Month folder.
6. The script uses multi-threading to process multiple files concurrently, significantly improving performance for large collections.

## Notes

- This script will modify the file structure in the source folder. It's recommended to backup your files before running this script.
- The script preserves the original filenames of the photos.
- While designed for DNG and CR2 files, you can easily modify the script to include other raw formats by editing the file extension check in the `get_raw_files` function.

## Contributing

Feel free to fork this repository and submit pull requests with any enhancements.

## License

[MIT License](LICENSE)
