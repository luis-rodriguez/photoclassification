# Roadmap

This document outlines planned features and enhancements for Photo Date Classifier.

## Version 0.2.0 (Q1 2025)

### Smart Time Correction
- [ ] Timezone inference from camera model database
- [ ] User-specified timezone offsets
- [ ] Automatic DST handling
- [ ] Bulk time correction for mis-dated photos
- [ ] Time correction from GPS data

### Enhanced Duplicate Detection
- [ ] Persistent duplicate index (SQLite)
- [ ] Visual similarity detection (perceptual hashing)
- [ ] Smart merging of duplicate sets
- [ ] Duplicate manifest export (CSV/JSONL)

### Sidecar Support
- [ ] XMP sidecar reading
- [ ] XMP sidecar writing (opt-in)
- [ ] Date correction in sidecars
- [ ] Metadata synchronization

## Version 0.3.0 (Q2 2025)

### Watch Mode
- [ ] inotify support (Linux)
- [ ] FSEvents support (macOS)
- [ ] File system watcher (cross-platform fallback)
- [ ] Automatic classification of new files
- [ ] Configurable watch directories
- [ ] Daemon mode

### Advanced Organization
- [ ] Pluggable destination strategies via entry points
- [ ] Smart folder naming (event detection)
- [ ] GPS-based location folders
- [ ] Custom metadata-based organization
- [ ] Album/collection support

### Performance Improvements
- [ ] Incremental processing (skip already-organized)
- [ ] Database for tracking processed files
- [ ] Parallel I/O optimization
- [ ] Memory-mapped file operations
- [ ] Progress persistence (resume after crash)

## Version 0.4.0 (Q3 2025)

### Cloud Storage
- [ ] S3 backend support
- [ ] Google Cloud Storage support
- [ ] Azure Blob Storage support
- [ ] Checksum manifest generation
- [ ] Sync capabilities
- [ ] Bandwidth throttling

### HEIF/HEIC Support
- [ ] HEIF metadata reading (via pillow-heif)
- [ ] HEIC Live Photo support
- [ ] HDR metadata handling
- [ ] Codec detection and validation

### Verification Tools
- [ ] Verify organization integrity
- [ ] Detect moved/renamed files
- [ ] Re-link duplicates
- [ ] Checksum verification mode
- [ ] Orphaned file detection

## Version 0.5.0 (Q4 2025)

### GUI/TUI
- [ ] Terminal UI with rich/textual
- [ ] Web UI (Flask/FastAPI)
- [ ] Desktop GUI (Qt/Tkinter)
- [ ] Real-time progress visualization
- [ ] Interactive duplicate resolution
- [ ] Configuration GUI

### Internationalization
- [ ] i18n framework setup (gettext)
- [ ] Localized CLI messages
- [ ] Localized folder names (optional)
- [ ] Date format localization
- [ ] Multiple language support

### Advanced Features
- [ ] Smart event detection (date clustering)
- [ ] Face detection integration (optional)
- [ ] GPS track matching
- [ ] Weather data enrichment
- [ ] Social media integration (import/export)

## Future Considerations

### Machine Learning
- [ ] Smart photo categorization
- [ ] Scene detection
- [ ] Quality scoring
- [ ] Auto-tagging

### Integration
- [ ] Lightroom catalog import/export
- [ ] Capture One integration
- [ ] Photo management software plugins
- [ ] DAM system integration

### Mobile
- [ ] Android app
- [ ] iOS app
- [ ] Mobile web interface
- [ ] Remote management

### Enterprise Features
- [ ] Multi-user support
- [ ] Access control
- [ ] Audit logging
- [ ] Backup/restore automation
- [ ] Policy enforcement

## Contributing

We welcome contributions for any of these features! Please:

1. Check if work is already in progress
2. Open an issue to discuss your approach
3. Submit a PR following our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines

## Voting

Want to prioritize a feature? Vote by:
- Adding a 👍 reaction to the corresponding issue
- Commenting with your use case
- Sponsoring development

## Stability

We aim to maintain:
- Semantic versioning
- Backward compatibility within major versions
- Clear migration guides for breaking changes
- Long-term support for LTS versions

---

*Last updated: 2024-10-21*
