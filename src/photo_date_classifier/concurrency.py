"""Thread pool utilities and concurrency management."""

import os
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from typing import Callable, TypeVar

from tqdm import tqdm

from .logging_setup import get_logger

logger = get_logger("concurrency")

T = TypeVar("T")
R = TypeVar("R")


def get_optimal_concurrency(user_concurrency: int = 0) -> int:
    """
    Determine optimal concurrency level.

    Args:
        user_concurrency: User-specified concurrency (0 for auto)

    Returns:
        Optimal number of worker threads
    """
    if user_concurrency > 0:
        return user_concurrency

    # Default: CPU count + 4 (I/O bound workload)
    cpu_count = os.cpu_count() or 4
    return min(cpu_count + 4, 32)


def process_files_concurrently(
    files: Iterable[T],
    processor: Callable[[T], R],
    max_workers: int = 0,
    desc: str = "Processing files",
    show_progress: bool = True,
) -> list[R]:
    """
    Process files concurrently with a thread pool.

    Args:
        files: Iterable of file paths to process
        processor: Function to process each file
        max_workers: Maximum number of worker threads (0 for auto)
        desc: Description for progress bar
        show_progress: Whether to show progress bar

    Returns:
        List of results from processing each file
    """
    files_list = list(files)
    total = len(files_list)

    if total == 0:
        logger.info("No files to process")
        return []

    workers = get_optimal_concurrency(max_workers)
    logger.info(f"Processing {total} files with {workers} workers")

    results: list[R] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_file = {executor.submit(processor, file): file for file in files_list}

        # Process results as they complete
        if show_progress:
            with tqdm(total=total, desc=desc, unit="file") as pbar:
                for future in as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error processing {file}: {e}")
                    finally:
                        pbar.update(1)
        else:
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")

    return results
