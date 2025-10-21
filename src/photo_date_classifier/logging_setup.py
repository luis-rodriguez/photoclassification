"""Logging configuration for photo classification."""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", json_output: bool = False) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Whether to output logs in JSON format
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("photo_date_classifier")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    if json_output:
        # Simple JSON-like format for now
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to photo_date_classifier)
        
    Returns:
        Logger instance
    """
    if name is None:
        return logging.getLogger("photo_date_classifier")
    return logging.getLogger(f"photo_date_classifier.{name}")
