"""Tests for hashing module."""

from pathlib import Path

from photo_date_classifier.hashing import are_files_identical, compute_file_hash


def test_compute_file_hash(tmp_path: Path) -> None:
    """Test file hash computation."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    # SHA256 of "hello world"
    expected_hash = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    result = compute_file_hash(test_file, "sha256")
    assert result == expected_hash


def test_are_files_identical(tmp_path: Path) -> None:
    """Test file identity comparison."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "file3.txt"

    file1.write_text("same content")
    file2.write_text("same content")
    file3.write_text("different content")

    assert are_files_identical(file1, file2) is True
    assert are_files_identical(file1, file3) is False


def test_are_files_identical_different_sizes(tmp_path: Path) -> None:
    """Test file identity with different sizes."""
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_text("short")
    file2.write_text("much longer content")

    # Should return False quickly without computing hashes
    assert are_files_identical(file1, file2) is False
