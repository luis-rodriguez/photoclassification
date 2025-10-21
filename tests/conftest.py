"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_config_data():
    """Sample configuration data for testing."""
    return {
        "source": "/path/to/source",
        "destination": "/path/to/dest",
        "structure": "{year}/{month}",
        "extensions": [".dng", ".cr2"],
        "concurrency": 4,
    }
