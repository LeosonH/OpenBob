"""Logging configuration for the application."""
import logging
import sys
from pathlib import Path

from config import LOG_FILE, LOG_LEVEL, LOG_FORMAT


def setup_logging(log_to_file: bool = True, log_to_console: bool = True):
    """Configure logging for the application.

    Args:
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Add file handler
    if log_to_file:
        try:
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(getattr(logging, LOG_LEVEL))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}", file=sys.stderr)

    # Add console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    logging.info("Logging initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__ of the module)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
