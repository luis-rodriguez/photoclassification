"""Photo Date Classifier - Organize photos by date using EXIF data."""

__version__ = "0.1.0"
__author__ = "Luis Rodriguez"
__description__ = "Organize photos by date using EXIF data"

from .models import ClassificationResult, Config, DuplicatePolicy, Operation, Photo

__all__ = [
    "Photo",
    "ClassificationResult",
    "Config",
    "DuplicatePolicy",
    "Operation",
    "__version__",
]
