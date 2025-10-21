"""File organization and path management."""
import os
import shutil
from pathlib import Path
from typing import Optional

from .hashing import are_files_identical
from .logging_setup import get_logger
from .models import ClassificationResult, Config, DuplicatePolicy, Operation, Photo

logger = get_logger("organizer")


def sanitize_path_component(component: str) -> str:
    """
    Sanitize a path component to prevent path traversal.
    
    Args:
        component: Path component to sanitize
        
    Returns:
        Sanitized path component
    """
    # Remove path traversal attempts
    sanitized = component.replace("..", "").replace("/", "-").replace("\\", "-")
    
    # Remove other problematic characters
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in (" ", "-", "_", "."))
    
    return sanitized.strip()


def format_destination_path(photo: Photo, config: Config) -> Path:
    """
    Generate destination path for a photo based on template.
    
    Args:
        photo: Photo object with metadata
        config: Configuration with structure template
        
    Returns:
        Destination path
    """
    if photo.date_taken is None:
        raise ValueError(f"Photo {photo.path} has no date information")
    
    # Extract date components
    date = photo.date_taken
    
    # Build context for template formatting
    context = {
        "year": str(date.year),
        "month": f"{date.month:02d}",
        "day": f"{date.day:02d}",
        "hour": f"{date.hour:02d}",
        "minute": f"{date.minute:02d}",
        "second": f"{date.second:02d}",
        "camera_model": sanitize_path_component(photo.camera_model or "Unknown"),
        "ext": photo.path.suffix.lower(),
        "iso": str(photo.iso) if photo.iso else "unknown",
    }
    
    # Format the structure template
    try:
        structure = config.structure_template.format(**context)
    except KeyError as e:
        logger.warning(f"Invalid template key {e}, falling back to year/month")
        structure = f"{context['year']}/{context['month']}"
    
    # Sanitize each path component
    parts = structure.split("/")
    sanitized_parts = [sanitize_path_component(part) for part in parts if part]
    
    # Build destination directory
    dest_dir = config.destination
    for part in sanitized_parts:
        dest_dir = dest_dir / part
    
    # Handle filename
    filename = photo.path.name
    
    # Apply rename pattern if configured
    if config.rename_pattern:
        try:
            original_stem = photo.path.stem
            original_ext = photo.path.suffix
            time_str = date.strftime("%Y-%m-%d-%H%M%S")
            
            # Build context for filename
            name_context = {
                "year": str(date.year),
                "month": f"{date.month:02d}",
                "day": f"{date.day:02d}",
                "time": time_str,
                "original": original_stem,
                "ext": original_ext.lstrip("."),
            }
            
            filename = config.rename_pattern.format(**name_context)
            if not filename.endswith(original_ext):
                filename = f"{filename}{original_ext}"
        except Exception as e:
            logger.warning(f"Failed to apply rename pattern: {e}, using original filename")
            filename = photo.path.name
    
    return dest_dir / filename


def get_unique_destination(base_path: Path) -> Path:
    """
    Get a unique destination path by appending a suffix if needed.
    
    Args:
        base_path: Desired destination path
        
    Returns:
        Unique destination path
    """
    if not base_path.exists():
        return base_path
    
    # File exists, append suffix
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    
    counter = 1
    while True:
        new_path = parent / f"{stem}-{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def check_if_duplicate(source: Path, destination: Path, config: Config) -> bool:
    """
    Check if a file is a duplicate of an existing file.
    
    Args:
        source: Source file path
        destination: Destination file path
        config: Configuration
        
    Returns:
        True if the file is a duplicate
    """
    if not destination.exists():
        return False
    
    # Check if files are identical
    if config.duplicate_policy == DuplicatePolicy.SKIP:
        # For skip policy, just check if file already exists at destination
        return are_files_identical(source, destination)
    
    return False


def safe_copy_file(source: Path, destination: Path) -> None:
    """
    Safely copy a file with atomic operations where possible.
    
    Args:
        source: Source file path
        destination: Destination file path
    """
    # Ensure destination directory exists
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy file with metadata
    shutil.copy2(source, destination)
    
    # Sync to disk
    try:
        fd = os.open(destination, os.O_RDONLY)
        os.fsync(fd)
        os.close(fd)
    except (OSError, AttributeError):
        # fsync may not be available on all platforms
        pass


def safe_move_file(source: Path, destination: Path) -> None:
    """
    Safely move a file (copy then delete).
    
    Args:
        source: Source file path
        destination: Destination file path
    """
    # First copy the file
    safe_copy_file(source, destination)
    
    # Then remove the source
    try:
        source.unlink()
    except Exception as e:
        logger.error(f"Failed to delete source file {source} after copy: {e}")
        raise


def execute_operation(result: ClassificationResult, config: Config) -> None:
    """
    Execute the file operation (move, copy, or hardlink).
    
    Args:
        result: Classification result with source and destination
        config: Configuration with operation type
    """
    if result.skipped or result.error:
        return
    
    if config.dry_run:
        logger.info(f"[DRY RUN] Would {config.operation.value} {result.source} -> {result.destination}")
        return
    
    try:
        if config.operation == Operation.MOVE:
            safe_move_file(result.source, result.destination)
            logger.info(f"Moved {result.source} -> {result.destination}")
        elif config.operation == Operation.COPY:
            safe_copy_file(result.source, result.destination)
            logger.info(f"Copied {result.source} -> {result.destination}")
        elif config.operation == Operation.HARDLINK:
            result.destination.parent.mkdir(parents=True, exist_ok=True)
            if result.destination.exists():
                result.destination.unlink()
            os.link(result.source, result.destination)
            logger.info(f"Hardlinked {result.source} -> {result.destination}")
    except Exception as e:
        logger.error(f"Failed to {config.operation.value} {result.source}: {e}")
        result.error = str(e)
        raise


def classify_photo(photo: Photo, config: Config) -> ClassificationResult:
    """
    Classify a single photo and determine its destination.
    
    Args:
        photo: Photo object with metadata
        config: Configuration
        
    Returns:
        Classification result
    """
    try:
        # Generate destination path
        dest_path = format_destination_path(photo, config)
        
        # Check for duplicates
        is_duplicate = check_if_duplicate(photo.path, dest_path, config)
        
        # Handle collision - get unique path if needed
        if dest_path.exists() and not is_duplicate:
            dest_path = get_unique_destination(dest_path)
        
        result = ClassificationResult(
            source=photo.path,
            destination=dest_path,
            photo=photo,
            is_duplicate=is_duplicate,
        )
        
        # Apply duplicate policy
        if is_duplicate:
            if config.duplicate_policy == DuplicatePolicy.SKIP:
                result.skipped = True
                result.skipped_reason = "Duplicate file"
                logger.debug(f"Skipping duplicate: {photo.path}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to classify {photo.path}: {e}")
        return ClassificationResult(
            source=photo.path,
            destination=photo.path,  # dummy destination
            photo=photo,
            error=str(e),
        )
