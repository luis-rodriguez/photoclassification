"""Data models for photo classification."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class DuplicatePolicy(Enum):
    """Policy for handling duplicate files."""

    SKIP = "skip"
    KEEP_FIRST = "keep-first"
    QUARANTINE = "quarantine"
    MANIFEST = "manifest"


class Operation(Enum):
    """Type of file operation."""

    MOVE = "move"
    COPY = "copy"
    HARDLINK = "hardlink"


@dataclass
class Photo:
    """Represents a photo file with metadata."""

    path: Path
    date_taken: Optional[datetime] = None
    camera_model: Optional[str] = None
    file_size: int = 0
    content_hash: Optional[str] = None
    exif_source: str = "unknown"  # datetime_original, create_date, modify_date, mtime
    iso: Optional[int] = None
    
    def __post_init__(self) -> None:
        """Initialize computed fields."""
        if not self.path.exists():
            raise ValueError(f"Photo file does not exist: {self.path}")
        if self.file_size == 0:
            self.file_size = self.path.stat().st_size


@dataclass
class ClassificationResult:
    """Result of classifying a single photo."""

    source: Path
    destination: Path
    photo: Photo
    is_duplicate: bool = False
    duplicate_of: Optional[Path] = None
    error: Optional[str] = None
    skipped: bool = False
    skipped_reason: Optional[str] = None


@dataclass
class Config:
    """Configuration for photo classification."""

    source: Path
    destination: Path
    structure_template: str = "{year}/{month}"
    extensions: list[str] = field(default_factory=lambda: [".dng", ".cr2", ".nef", ".arw", ".raf", ".orf", ".rw2"])
    rename_pattern: Optional[str] = None  # e.g., "{year}-{month}-{day}-{time}_{original}"
    operation: Operation = Operation.MOVE
    dry_run: bool = False
    concurrency: int = 4
    duplicate_policy: DuplicatePolicy = DuplicatePolicy.SKIP
    follow_symlinks: bool = False
    log_level: str = "INFO"
    json_output: bool = False
    config_file: Optional[Path] = None
    
    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.source.exists():
            raise ValueError(f"Source directory does not exist: {self.source}")
        if not self.source.is_dir():
            raise ValueError(f"Source is not a directory: {self.source}")
        
        # Normalize extensions to lowercase
        self.extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                          for ext in self.extensions]
