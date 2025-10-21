"""Tests for organizer module."""
from datetime import datetime
from pathlib import Path

import pytest

from photo_date_classifier.models import Config, DuplicatePolicy, Operation, Photo
from photo_date_classifier.organizer import (
    format_destination_path,
    get_unique_destination,
    sanitize_path_component,
)


def test_sanitize_path_component() -> None:
    """Test path component sanitization."""
    assert sanitize_path_component("normal_name") == "normal_name"
    assert sanitize_path_component("../../../etc/passwd") == "etcpasswd"
    assert sanitize_path_component("test/path") == "test-path"
    assert sanitize_path_component("test\\path") == "test-path"


def test_format_destination_path_basic(tmp_path: Path) -> None:
    """Test basic destination path formatting."""
    config = Config(
        source=tmp_path / "source",
        destination=tmp_path / "dest",
        structure_template="{year}/{month}",
    )
    config.source.mkdir()
    
    photo = Photo(
        path=tmp_path / "source" / "test.dng",
        date_taken=datetime(2023, 10, 21, 14, 30, 45),
    )
    photo.path.parent.mkdir(exist_ok=True)
    photo.path.write_bytes(b"test")
    
    dest = format_destination_path(photo, config)
    
    assert dest.parent.name == "10"
    assert dest.parent.parent.name == "2023"
    assert dest.name == "test.dng"


def test_format_destination_path_with_rename(tmp_path: Path) -> None:
    """Test destination path with rename pattern."""
    config = Config(
        source=tmp_path / "source",
        destination=tmp_path / "dest",
        structure_template="{year}/{month}",
        rename_pattern="{year}-{month}-{day}-{time}_{original}.{ext}",
    )
    config.source.mkdir()
    
    photo = Photo(
        path=tmp_path / "source" / "test.dng",
        date_taken=datetime(2023, 10, 21, 14, 30, 45),
    )
    photo.path.parent.mkdir(exist_ok=True)
    photo.path.write_bytes(b"test")
    
    dest = format_destination_path(photo, config)
    
    assert dest.name == "2023-10-21-2023-10-21-143045_test.dng.dng"


def test_format_destination_path_with_camera(tmp_path: Path) -> None:
    """Test destination path with camera model."""
    config = Config(
        source=tmp_path / "source",
        destination=tmp_path / "dest",
        structure_template="{year}/{camera_model}/{month}",
    )
    config.source.mkdir()
    
    photo = Photo(
        path=tmp_path / "source" / "test.dng",
        date_taken=datetime(2023, 10, 21, 14, 30, 45),
        camera_model="Canon EOS 5D",
    )
    photo.path.parent.mkdir(exist_ok=True)
    photo.path.write_bytes(b"test")
    
    dest = format_destination_path(photo, config)
    
    assert "Canon EOS 5D" in str(dest)
    assert dest.parent.name == "10"


def test_get_unique_destination(tmp_path: Path) -> None:
    """Test getting unique destination path."""
    base = tmp_path / "test.dng"
    
    # First call should return the same path
    assert get_unique_destination(base) == base
    
    # Create the file and try again
    base.write_bytes(b"test")
    unique = get_unique_destination(base)
    
    assert unique != base
    assert unique.stem == "test-1"
    assert unique.suffix == ".dng"
