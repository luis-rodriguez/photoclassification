"""Command-line interface for photo-date-classifier."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from . import __version__
from .concurrency import process_files_concurrently
from .exif_reader import extract_photo_metadata
from .hashing import compute_file_hash
from .logging_setup import get_logger, setup_logging
from .models import Config, DuplicatePolicy, Operation
from .organizer import classify_photo, execute_operation

logger = get_logger()


def find_photo_files(
    source: Path, extensions: list[str], follow_symlinks: bool = False
) -> list[Path]:
    """
    Find all photo files in a directory tree.

    Args:
        source: Source directory
        extensions: List of file extensions to include
        follow_symlinks: Whether to follow symbolic links

    Returns:
        List of photo file paths
    """
    photo_files = []

    for item in source.rglob("*"):
        if item.is_file():
            if not follow_symlinks and item.is_symlink():
                continue
            if item.suffix.lower() in extensions:
                photo_files.append(item)

    return photo_files


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """Photo Date Classifier - Organize photos by date using EXIF data."""
    pass


@main.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Source directory containing photos",
)
@click.option(
    "--dest",
    "-d",
    type=click.Path(path_type=Path),
    required=True,
    help="Destination directory for organized photos",
)
@click.option(
    "--structure",
    default="{year}/{month}",
    help="Output structure template (e.g., {year}/{month}, {year}/{camera_model}/{month})",
)
@click.option(
    "--extensions",
    default=".dng,.cr2,.nef,.arw,.raf,.orf,.rw2",
    help="Comma-separated list of file extensions to process",
)
@click.option(
    "--rename",
    default=None,
    help="Rename pattern (e.g., {year}-{month}-{day}-{time}_{original}.{ext})",
)
@click.option(
    "--operation",
    type=click.Choice(["move", "copy", "hardlink"], case_sensitive=False),
    default="move",
    help="File operation to perform",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "--concurrency",
    "-j",
    type=int,
    default=0,
    help="Number of concurrent workers (0 for auto)",
)
@click.option(
    "--duplicate-policy",
    type=click.Choice(["skip", "keep-first", "quarantine", "manifest"], case_sensitive=False),
    default="skip",
    help="Policy for handling duplicate files",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Logging level",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output results in JSON format",
)
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to YAML configuration file",
)
def classify(
    source: Path,
    dest: Path,
    structure: str,
    extensions: str,
    rename: Optional[str],
    operation: str,
    dry_run: bool,
    concurrency: int,
    duplicate_policy: str,
    log_level: str,
    json_output: bool,
    config: Optional[Path],
) -> None:
    """Classify and organize photos by date."""
    # Setup logging
    setup_logging(log_level, json_output)

    # Load config from file if provided
    if config:
        try:
            with open(config) as f:
                yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config}")
            # Override with config file values where not explicitly set
            # (CLI args take precedence)
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            sys.exit(1)

    # Parse extensions
    ext_list = [ext.strip() for ext in extensions.split(",")]

    # Create configuration
    try:
        cfg = Config(
            source=source,
            destination=dest,
            structure_template=structure,
            extensions=ext_list,
            rename_pattern=rename,
            operation=Operation[operation.upper()],
            dry_run=dry_run,
            concurrency=concurrency,
            duplicate_policy=DuplicatePolicy[duplicate_policy.upper().replace("-", "_")],
            log_level=log_level,
            json_output=json_output,
            config_file=config,
        )
    except Exception as e:
        logger.error(f"Invalid configuration: {e}")
        sys.exit(1)

    logger.info(f"Classifying photos from {source} to {dest}")
    logger.info(f"Structure template: {structure}")
    logger.info(f"Operation: {operation} (dry_run={dry_run})")

    # Find photo files
    logger.info("Scanning for photo files...")
    photo_files = find_photo_files(source, cfg.extensions, cfg.follow_symlinks)

    if not photo_files:
        logger.warning("No photo files found matching criteria")
        return

    logger.info(f"Found {len(photo_files)} photo files")

    # Extract metadata from all photos
    logger.info("Extracting metadata...")
    photos = process_files_concurrently(
        photo_files,
        extract_photo_metadata,
        max_workers=cfg.concurrency,
        desc="Reading EXIF data",
    )

    # Classify photos
    logger.info("Classifying photos...")

    def classify_with_config(photo):  # type: ignore
        return classify_photo(photo, cfg)

    results = process_files_concurrently(
        photos,
        classify_with_config,
        max_workers=cfg.concurrency,
        desc="Classifying photos",
    )

    # Filter out errors and skipped
    successful_results = [r for r in results if not r.error and not r.skipped]
    skipped_results = [r for r in results if r.skipped]
    error_results = [r for r in results if r.error]

    logger.info("Classification complete:")
    logger.info(f"  - Successful: {len(successful_results)}")
    logger.info(f"  - Skipped: {len(skipped_results)}")
    logger.info(f"  - Errors: {len(error_results)}")

    # Execute operations
    if not dry_run and successful_results:
        logger.info("Executing file operations...")
        for result in successful_results:
            try:
                execute_operation(result, cfg)
            except Exception as e:
                logger.error(f"Failed to process {result.source}: {e}")

    # Output summary
    if json_output:
        output = {
            "total": len(results),
            "successful": len(successful_results),
            "skipped": len(skipped_results),
            "errors": len(error_results),
            "results": [
                {
                    "source": str(r.source),
                    "destination": str(r.destination),
                    "skipped": r.skipped,
                    "error": r.error,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        if dry_run:
            logger.info("\n[DRY RUN] No changes were made")
        else:
            logger.info("\nClassification complete!")

    # Exit with error code if there were errors
    if error_results:
        sys.exit(1)


@main.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Source directory containing photos",
)
@click.option(
    "--dest",
    "-d",
    type=click.Path(path_type=Path),
    required=True,
    help="Destination directory for organized photos",
)
@click.option(
    "--structure",
    default="{year}/{month}",
    help="Output structure template",
)
@click.option(
    "--extensions",
    default=".dng,.cr2,.nef,.arw,.raf,.orf,.rw2",
    help="Comma-separated list of file extensions",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output plan in JSON format",
)
def plan(
    source: Path,
    dest: Path,
    structure: str,
    extensions: str,
    json_output: bool,
) -> None:
    """Generate a classification plan without making changes."""
    setup_logging("INFO", json_output)

    # Parse extensions
    ext_list = [ext.strip() for ext in extensions.split(",")]

    # Create configuration with dry_run enabled
    cfg = Config(
        source=source,
        destination=dest,
        structure_template=structure,
        extensions=ext_list,
        dry_run=True,
        concurrency=4,
    )

    logger.info("Generating classification plan...")

    # Find and process photos
    photo_files = find_photo_files(source, cfg.extensions, False)

    if not photo_files:
        logger.warning("No photo files found")
        return

    photos = process_files_concurrently(
        photo_files,
        extract_photo_metadata,
        max_workers=cfg.concurrency,
        desc="Reading EXIF data",
        show_progress=not json_output,
    )

    def classify_with_config(photo):  # type: ignore
        return classify_photo(photo, cfg)

    results = process_files_concurrently(
        photos,
        classify_with_config,
        max_workers=cfg.concurrency,
        desc="Planning classification",
        show_progress=not json_output,
    )

    # Output plan
    if json_output:
        output = {
            "total": len(results),
            "operations": [
                {
                    "source": str(r.source),
                    "destination": str(r.destination),
                    "size": r.photo.file_size,
                    "date_taken": r.photo.date_taken.isoformat() if r.photo.date_taken else None,
                    "is_duplicate": r.is_duplicate,
                }
                for r in results
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nClassification Plan ({len(results)} files):\n")
        for r in results[:10]:  # Show first 10
            print(f"  {r.source} -> {r.destination}")
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")


@main.command()
@click.option(
    "--directory",
    "-d",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Directory to hash files in",
)
@click.option(
    "--extensions",
    default=".dng,.cr2,.nef,.arw,.raf,.orf,.rw2",
    help="Comma-separated list of file extensions",
)
@click.option(
    "--algorithm",
    default="sha256",
    help="Hash algorithm to use",
)
def hash(directory: Path, extensions: str, algorithm: str) -> None:
    """Compute and list file hashes."""
    setup_logging("INFO", False)

    ext_list = [ext.strip() for ext in extensions.split(",")]

    logger.info(f"Computing {algorithm} hashes for files in {directory}")

    # Find files
    files = []
    for item in directory.rglob("*"):
        if item.is_file() and item.suffix.lower() in ext_list:
            files.append(item)

    if not files:
        logger.warning("No files found")
        return

    # Compute hashes
    for file in files:
        try:
            file_hash = compute_file_hash(file, algorithm)
            print(f"{file_hash}  {file}")
        except Exception as e:
            logger.error(f"Failed to hash {file}: {e}")


if __name__ == "__main__":
    main()
