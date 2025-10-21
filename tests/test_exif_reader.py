"""Tests for EXIF reader module."""
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from photo_date_classifier.exif_reader import (
    extract_photo_metadata,
    parse_exif_datetime,
    sanitize_camera_model,
)
from photo_date_classifier.models import Photo


def test_sanitize_camera_model() -> None:
    """Test camera model sanitization."""
    assert sanitize_camera_model("Canon EOS 5D") == "Canon EOS 5D"
    assert sanitize_camera_model("  Nikon D850  ") == "Nikon D850"
    assert sanitize_camera_model("Sony/A7III") == "Sony-A7III"
    assert sanitize_camera_model("Test\\Model") == "Test-Model"
    assert sanitize_camera_model("") is None
    assert sanitize_camera_model(None) is None


def test_parse_exif_datetime() -> None:
    """Test EXIF datetime parsing."""
    result = parse_exif_datetime("2023:10:21 14:30:45")
    assert result == datetime(2023, 10, 21, 14, 30, 45)
    
    # Invalid format should return None
    assert parse_exif_datetime("invalid") is None
    assert parse_exif_datetime("") is None


def test_extract_photo_metadata_no_exif(tmp_path: Path) -> None:
    """Test metadata extraction from file without EXIF."""
    # Create a test file
    test_file = tmp_path / "test.dng"
    test_file.write_bytes(b"fake image data")
    
    with patch("photo_date_classifier.exif_reader.exif.Image") as mock_image_class:
        mock_image = MagicMock()
        mock_image.has_exif = False
        mock_image_class.return_value = mock_image
        
        photo = extract_photo_metadata(test_file)
        
        assert photo.path == test_file
        assert photo.date_taken is not None
        assert photo.exif_source == "mtime"


def test_extract_photo_metadata_with_exif(tmp_path: Path) -> None:
    """Test metadata extraction from file with EXIF."""
    test_file = tmp_path / "test.dng"
    test_file.write_bytes(b"fake image data")
    
    with patch("photo_date_classifier.exif_reader.exif.Image") as mock_image_class:
        mock_image = MagicMock()
        mock_image.has_exif = True
        mock_image.datetime_original = "2023:10:21 14:30:45"
        mock_image.model = "Canon EOS 5D"
        mock_image.photographic_sensitivity = 400
        mock_image_class.return_value = mock_image
        
        photo = extract_photo_metadata(test_file)
        
        assert photo.path == test_file
        assert photo.date_taken == datetime(2023, 10, 21, 14, 30, 45)
        assert photo.exif_source == "datetime_original"
        assert photo.camera_model == "Canon EOS 5D"
        assert photo.iso == 400
