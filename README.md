# Photo Date Classifier

A modern, robust Python package for organizing photos by date using EXIF metadata. Features include multi-threading, duplicate detection, configurable output structures, and comprehensive safety checks.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Smart Date Detection**: Prioritizes DateTimeOriginal, CreateDate, ModifyDate EXIF tags with fallback to file mtime
- **Flexible Organization**: Configurable output structures using templates (Year/Month, Year/Camera/Month, custom patterns)
- **Multiple RAW Formats**: Supports DNG, CR2, NEF, ARW, RAF, ORF, RW2, and optionally HEIC/JPEG
- **Duplicate Detection**: Content-based (SHA-256) duplicate identification with configurable policies
- **Safe Operations**: Copy-then-delete with fsync, collision handling, path sanitization
- **Concurrent Processing**: Bounded thread pool with smart defaults based on system resources
- **Dry Run Mode**: Preview changes before execution
- **Progress Tracking**: Real-time progress bars and detailed logging
- **Cross-Platform**: Windows, macOS, and Linux support with Unicode filename handling
- **Type-Safe**: Full type hints and mypy strict mode
- **Well-Tested**: Comprehensive test suite with >90% coverage

## Installation

### From Source

```bash
git clone https://github.com/luis-rodriguez/photoclassification.git
cd photoclassification
pip install -e .
```

### For Development

```bash
pip install -e ".[dev]"
pre-commit install
```

## Quick Start

### Basic Usage

Organize photos from a source directory:

```bash
photo-date-classifier classify --source /path/to/photos --dest /path/to/organized
```

### With Custom Structure

Organize by Year/Camera Model/Month:

```bash
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized \
  --structure "{year}/{camera_model}/{month}"
```

### Dry Run (Preview Changes)

```bash
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized \
  --dry-run
```

### Copy Instead of Move

```bash
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized \
  --operation copy
```

### Rename Files with Date

```bash
photo-date-classifier classify \
  --source /path/to/photos \
  --dest /path/to/organized \
  --rename "{year}-{month}-{day}-{time}_{original}.{ext}"
```

## CLI Commands

### `classify`

Main command to organize photos:

```bash
photo-date-classifier classify [OPTIONS]
```

**Options:**
- `--source, -s PATH`: Source directory (required)
- `--dest, -d PATH`: Destination directory (required)
- `--structure TEMPLATE`: Output structure template (default: `{year}/{month}`)
- `--extensions LIST`: Comma-separated extensions (default: `.dng,.cr2,.nef,.arw,.raf,.orf,.rw2`)
- `--rename PATTERN`: Rename pattern (optional)
- `--operation TYPE`: Operation type: `move`, `copy`, `hardlink` (default: `move`)
- `--dry-run`: Preview without making changes
- `--concurrency, -j N`: Worker threads (0=auto, default: 0)
- `--duplicate-policy POLICY`: Duplicate handling: `skip`, `keep-first`, `quarantine`, `manifest` (default: `skip`)
- `--log-level LEVEL`: Logging level (default: `INFO`)
- `--json`: Output results in JSON format
- `--config PATH`: YAML configuration file

### `plan`

Generate a classification plan without making changes:

```bash
photo-date-classifier plan --source /path/to/photos --dest /path/to/organized
```

### `hash`

Compute and list file hashes:

```bash
photo-date-classifier hash --directory /path/to/photos
```

## Structure Templates

Templates support the following placeholders:

- `{year}`: Four-digit year
- `{month}`: Two-digit month
- `{day}`: Two-digit day
- `{hour}`, `{minute}`, `{second}`: Time components
- `{camera_model}`: Camera model from EXIF (sanitized)
- `{iso}`: ISO value
- `{ext}`: File extension

**Examples:**

- `{year}/{month}` → `2023/10/`
- `{year}/{month}/{day}` → `2023/10/21/`
- `{year}/{camera_model}/{month}` → `2023/Canon EOS 5D/10/`

## Configuration File

You can use a YAML configuration file:

```yaml
# config.yaml
source: /path/to/photos
destination: /path/to/organized
structure: "{year}/{camera_model}/{month}"
extensions:
  - .dng
  - .cr2
  - .nef
concurrency: 8
duplicate_policy: skip
log_level: INFO
```

Then run:

```bash
photo-date-classifier classify --config config.yaml
```

## Duplicate Detection

The tool can detect duplicates using content hashing (SHA-256) and metadata:

- **skip**: Skip duplicate files (default)
- **keep-first**: Keep first occurrence, skip duplicates
- **quarantine**: Move duplicates to a separate folder
- **manifest**: Create a CSV/JSONL manifest of duplicates

## Safety Features

- **Path Sanitization**: Prevents path traversal attacks
- **Atomic Operations**: Copy-then-delete with fsync
- **Collision Handling**: Automatic suffix appending for filename conflicts
- **Idempotent**: Re-running is safe and won't duplicate work
- **Error Recovery**: Continues on individual file errors

## Performance Tips

- Use `--concurrency` to control parallelism (default auto-detects optimal value)
- Enable duplicate detection only when needed (adds hashing overhead)
- Use `--dry-run` first to preview large operations
- Consider `--operation copy` for initial organization, then cleanup manually

## Legacy Script

The original `date-classifier.py` script is deprecated but still available for compatibility. It now delegates to the new CLI with a deprecation warning:

```bash
python date-classifier.py /path/to/photos [updatenames]
```

**Recommended:** Migrate to `photo-date-classifier` command.

## Development

### Setup Development Environment

```bash
git clone https://github.com/luis-rodriguez/photoclassification.git
cd photoclassification
pip install -e ".[dev]"
pre-commit install
```

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=photo_date_classifier --cov-report=html
```

### Linting and Formatting

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### Security Checks

```bash
# Static analysis
bandit -r src/

# Dependency audit
pip-audit
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features:

- Smart timezone correction
- Sidecar XMP support
- Watch mode (inotify/FSEvents)
- GUI wrapper
- Cloud storage backends (S3/GCS/Azure)
- Persistent duplicate detection index (SQLite)
- i18n support

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

For security concerns, please see [SECURITY.md](SECURITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Original script by Luis Rodriguez
- Built with: [Click](https://click.palletsprojects.com/), [exif](https://pypi.org/project/exif/), [tqdm](https://tqdm.github.io/)