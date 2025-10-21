#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated and will be removed in a future version.

Please use the new command-line interface instead:

    pip install -e .
    photo-date-classifier classify --source /path/to/photos --dest /path/to/organized

Or use the package directly from Python:

    from photo_date_classifier import Config
    from photo_date_classifier.cli import classify

For more information, see: https://github.com/luis-rodriguez/photoclassification
"""
import sys
import warnings
from pathlib import Path

warnings.warn(
    "date-classifier.py is deprecated. Please use 'photo-date-classifier' command instead.",
    DeprecationWarning,
    stacklevel=2,
)

print("=" * 80)
print("DEPRECATION WARNING")
print("=" * 80)
print()
print("This script (date-classifier.py) is deprecated and will be removed in a future version.")
print()
print("Please use the new photo-date-classifier command instead:")
print()
print("  Installation:")
print("    pip install -e .")
print()
print("  Usage:")
print("    photo-date-classifier classify --source <source> --dest <dest>")
print()
print("  For help:")
print("    photo-date-classifier --help")
print()
print("=" * 80)
print()

# Try to import and delegate to the new CLI
try:
    from photo_date_classifier.cli import main
    
    # Convert old-style arguments to new CLI format
    if len(sys.argv) >= 2:
        source = Path(sys.argv[1]).resolve()
        update_names = len(sys.argv) == 3 and sys.argv[2].lower() == "updatenames"
        
        # Build new-style arguments
        new_args = [
            "classify",
            "--source", str(source),
            "--dest", str(source),  # Organize in place (old behavior)
            "--operation", "move",
        ]
        
        if update_names:
            new_args.extend(["--rename", "{year}-{month}-{day}-{time}_{original}.{ext}"])
        
        sys.argv = ["photo-date-classifier"] + new_args
        
        print(f"Delegating to: photo-date-classifier {' '.join(new_args)}")
        print()
        
        main()
    else:
        print("Usage: python date-classifier.py <source_folder> [updatenames]")
        print()
        print("Or use the new CLI:")
        print("  photo-date-classifier classify --source <source> --dest <dest>")
        sys.exit(1)
        
except ImportError:
    print("ERROR: New photo-date-classifier package not installed.")
    print()
    print("Please install it first:")
    print("  pip install -e .")
    print()
    sys.exit(1)
