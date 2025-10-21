"""EXIF data extraction and date parsing."""
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import exif

from .logging_setup import get_logger
from .models import Photo

logger = get_logger("exif_reader")


def sanitize_camera_model(model: Optional[str]) -> Optional[str]:
    """
    Sanitize camera model string for use in file paths.
    
    Args:
        model: Raw camera model string
        
    Returns:
        Sanitized model string or None
    """
    if not model:
        return None
    
    # Strip whitespace and replace path separators
    sanitized = model.strip().replace("/", "-").replace("\\", "-")
    
    # Remove other problematic characters
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in (" ", "-", "_"))
    
    return sanitized.strip() if sanitized else None


def parse_exif_datetime(date_str: str) -> Optional[datetime]:
    """
    Parse EXIF datetime string.
    
    Args:
        date_str: EXIF datetime string (format: "YYYY:MM:DD HH:MM:SS")
        
    Returns:
        Parsed datetime or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
    except (ValueError, TypeError) as e:
        logger.debug(f"Failed to parse EXIF datetime '{date_str}': {e}")
        return None


def extract_photo_metadata(file_path: Path) -> Photo:
    """
    Extract metadata from a photo file.
    
    Tries to read EXIF data in the following priority:
    1. DateTimeOriginal
    2. CreateDate
    3. ModifyDate (DateTime)
    4. File modification time (fallback)
    
    Args:
        file_path: Path to the photo file
        
    Returns:
        Photo object with extracted metadata
    """
    photo = Photo(path=file_path)
    
    try:
        with open(file_path, "rb") as f:
            image = exif.Image(f)
        
        # Check if EXIF data is available
        if not image.has_exif:
            logger.debug(f"No EXIF data in {file_path}")
            photo.date_taken = datetime.fromtimestamp(file_path.stat().st_mtime)
            photo.exif_source = "mtime"
            return photo
        
        # Try DateTimeOriginal first (most reliable)
        if hasattr(image, "datetime_original"):
            date_taken = parse_exif_datetime(image.datetime_original)
            if date_taken:
                photo.date_taken = date_taken
                photo.exif_source = "datetime_original"
                logger.debug(f"Used DateTimeOriginal for {file_path}")
        
        # Try CreateDate if DateTimeOriginal not available
        if photo.date_taken is None and hasattr(image, "datetime_digitized"):
            date_taken = parse_exif_datetime(image.datetime_digitized)
            if date_taken:
                photo.date_taken = date_taken
                photo.exif_source = "datetime_digitized"
                logger.debug(f"Used DateTimeDigitized for {file_path}")
        
        # Try ModifyDate (DateTime tag) as last EXIF option
        if photo.date_taken is None and hasattr(image, "datetime"):
            date_taken = parse_exif_datetime(image.datetime)
            if date_taken:
                photo.date_taken = date_taken
                photo.exif_source = "datetime"
                logger.debug(f"Used DateTime for {file_path}")
        
        # Extract camera model if available
        if hasattr(image, "model"):
            photo.camera_model = sanitize_camera_model(image.model)
        
        # Extract ISO if available
        if hasattr(image, "photographic_sensitivity"):
            try:
                photo.iso = int(image.photographic_sensitivity)
            except (ValueError, TypeError):
                pass
        
    except Exception as e:
        logger.warning(f"Error reading EXIF from {file_path}: {e}")
    
    # Fallback to file modification time if no EXIF date found
    if photo.date_taken is None:
        photo.date_taken = datetime.fromtimestamp(file_path.stat().st_mtime)
        photo.exif_source = "mtime"
        logger.debug(f"Using mtime fallback for {file_path}")
    
    return photo


def get_photo_date_with_fallback(file_path: Path) -> Tuple[datetime, str]:
    """
    Get photo date with fallback chain.
    
    Args:
        file_path: Path to photo file
        
    Returns:
        Tuple of (datetime, source) where source indicates where the date came from
    """
    photo = extract_photo_metadata(file_path)
    return photo.date_taken, photo.exif_source  # type: ignore
