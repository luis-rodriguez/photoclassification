"""File hashing and duplicate detection."""
import hashlib
from pathlib import Path
from typing import Optional

from .logging_setup import get_logger

logger = get_logger("hashing")


def compute_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Compute hash of a file.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm to use (default: sha256)
        
    Returns:
        Hex digest of the file hash
    """
    hash_obj = hashlib.new(algorithm)
    
    try:
        with open(file_path, "rb") as f:
            # Read in chunks to handle large files
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception as e:
        logger.error(f"Failed to compute hash for {file_path}: {e}")
        raise


def compute_file_hash_if_needed(
    file_path: Path,
    current_hash: Optional[str] = None,
    algorithm: str = "sha256"
) -> str:
    """
    Compute file hash only if not already provided.
    
    Args:
        file_path: Path to file
        current_hash: Existing hash if available
        algorithm: Hash algorithm to use
        
    Returns:
        File hash (either provided or newly computed)
    """
    if current_hash:
        return current_hash
    return compute_file_hash(file_path, algorithm)


def are_files_identical(file1: Path, file2: Path) -> bool:
    """
    Check if two files are identical by comparing their content hashes.
    
    Args:
        file1: First file path
        file2: Second file path
        
    Returns:
        True if files have identical content
    """
    # Quick size check first
    if file1.stat().st_size != file2.stat().st_size:
        return False
    
    # Compare hashes
    hash1 = compute_file_hash(file1)
    hash2 = compute_file_hash(file2)
    
    return hash1 == hash2
