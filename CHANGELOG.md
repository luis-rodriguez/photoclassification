# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial package structure with src layout
- Modern CLI with Click framework
- Multiple subcommands: `classify`, `plan`, `hash`
- Type hints throughout codebase (mypy strict mode)
- Comprehensive test suite with pytest (>90% coverage)
- EXIF metadata extraction with fallback chain
- Configurable output structure templates
- Duplicate detection using SHA-256 content hashing
- Multiple duplicate policies: skip, keep-first, quarantine, manifest
- Dry-run mode for safe preview
- Concurrent processing with bounded thread pool
- Progress bars with tqdm
- Structured logging with configurable levels
- JSON output option for machine-readable results
- Support for multiple RAW formats: DNG, CR2, NEF, ARW, RAF, ORF, RW2
- Three operation modes: move, copy, hardlink
- Configurable filename rename patterns
- Safe file operations with copy-then-delete and fsync
- Collision handling with automatic suffix appending
- Path sanitization to prevent traversal attacks
- Cross-platform support (Windows, macOS, Linux)
- Unicode filename support
- YAML configuration file support
- Development tooling: Ruff, Black, Mypy, Bandit, pre-commit
- Security tooling: Bandit static analysis, pip-audit
- GitHub Actions CI pipeline
- CodeQL security scanning
- Dependabot configuration
- Comprehensive documentation (README, CONTRIBUTING, SECURITY)
- Legacy wrapper script with deprecation notice

### Changed
- Refactored from single-file script to installable package
- Replaced curses UI with progress bars and structured logging
- Improved error handling and recovery
- Enhanced concurrency management
- Better EXIF parsing with multiple tag fallbacks

### Deprecated
- Original `date-classifier.py` script (use `photo-date-classifier` CLI instead)

### Security
- Path traversal prevention
- Input validation and sanitization
- Secure file operations with atomic moves
- No shell execution to prevent injection
- Dependency pinning with compatible ranges

## [0.1.0] - 2024-10-21

Initial release of Photo Date Classifier as a modern Python package.

### Features
- Organize photos by date using EXIF metadata
- Multi-threaded processing for performance
- Support for RAW photo formats
- Configurable output structures
- Duplicate detection
- Dry-run mode
- Comprehensive tests and documentation
- CI/CD with security scanning

[Unreleased]: https://github.com/luis-rodriguez/photoclassification/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/luis-rodriguez/photoclassification/releases/tag/v0.1.0
