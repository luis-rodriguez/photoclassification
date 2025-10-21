"""Tests for models."""

from pathlib import Path

import pytest

from photo_date_classifier.models import Config, DuplicatePolicy, Operation


def test_config_validation(tmp_path: Path) -> None:
    """Test config validation."""
    source = tmp_path / "source"
    dest = tmp_path / "dest"
    source.mkdir()

    config = Config(source=source, destination=dest)

    assert config.source == source
    assert config.destination == dest
    assert config.operation == Operation.MOVE
    assert config.duplicate_policy == DuplicatePolicy.SKIP


def test_config_invalid_source(tmp_path: Path) -> None:
    """Test config with invalid source."""
    source = tmp_path / "nonexistent"
    dest = tmp_path / "dest"

    with pytest.raises(ValueError, match="does not exist"):
        Config(source=source, destination=dest)


def test_config_extensions_normalization(tmp_path: Path) -> None:
    """Test extension normalization."""
    source = tmp_path / "source"
    source.mkdir()

    config = Config(
        source=source,
        destination=tmp_path / "dest",
        extensions=["DNG", ".CR2", "nef"],
    )

    assert ".dng" in config.extensions
    assert ".cr2" in config.extensions
    assert ".nef" in config.extensions
