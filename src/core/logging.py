"""
Logging Module
==============

Centralized logging configuration for the entire application.

Features:
- Dual output: Console (terminal) and File
- Rotating file handler to prevent large log files
- Colored console output for better readability
- Full coverage across all modules

Author: CartWise Team
Version: 1.0.0
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime
from .config import settings


# ANSI color codes for terminal output
class LogColors:
    """ANSI color codes for colorized terminal logging."""

    RESET = "\033[0m"
    DEBUG = "\033[36m"      # Cyan
    INFO = "\033[32m"       # Green
    WARNING = "\033[33m"    # Yellow
    ERROR = "\033[31m"      # Red
    CRITICAL = "\033[35m"   # Magenta


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log levels in terminal output.
    """

    COLORS = {
        logging.DEBUG: LogColors.DEBUG,
        logging.INFO: LogColors.INFO,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.CRITICAL,
    }

    def format(self, record):
        """
        Format log record with color codes.

        Args:
            record: LogRecord instance

        Returns:
            Formatted and colored log string
        """
        # Add color to level name
        levelname = record.levelname
        if record.levelno in self.COLORS:
            levelname_color = (
                f"{self.COLORS[record.levelno]}{levelname}{LogColors.RESET}"
            )
            record.levelname = levelname_color

        # Format the message
        result = super().format(record)

        # Reset levelname for other handlers
        record.levelname = levelname

        return result


def setup_logging(
    level: Optional[str] = None,
    log_dir: str = "logs",
    log_file: str = "cartwise.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> None:
    """
    Configure logging for the entire application.

    Sets up dual logging:
    1. Console output with colors
    2. Rotating file output

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If not provided, uses LOG_LEVEL from settings
        log_dir: Directory for log files
        log_file: Log file name
        max_bytes: Max size of log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Example:
        >>> setup_logging()
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    log_level = level or settings.LOG_LEVEL

    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, log_file)

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # 1. Console Handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 2. File Handler (rotating, without colors)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Log the initialization
    root_logger.info("=" * 80)
    root_logger.info(f"Logging system initialized - Level: {log_level.upper()}")
    root_logger.info(f"Console output: Enabled (colored)")
    root_logger.info(f"File output: {log_path}")
    root_logger.info(f"Max file size: {max_bytes / 1024 / 1024:.1f}MB, Backups: {backup_count}")
    root_logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance configured with the application's logging settings

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing request")
        >>> logger.debug("Variable value: %s", my_var)
        >>> logger.error("Failed to process", exc_info=True)
    """
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs):
    """
    Helper function to log function entry with parameters.

    Args:
        logger: Logger instance
        func_name: Name of the function being called
        **kwargs: Function parameters to log

    Example:
        >>> logger = get_logger(__name__)
        >>> log_function_call(logger, "assign_cart", user_id=123, cart_id=5)
    """
    params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.debug(f">> Entering {func_name}({params})")


def log_function_exit(logger: logging.Logger, func_name: str, result=None):
    """
    Helper function to log function exit with result.

    Args:
        logger: Logger instance
        func_name: Name of the function exiting
        result: Return value (optional)

    Example:
        >>> logger = get_logger(__name__)
        >>> log_function_exit(logger, "assign_cart", result={"cart_id": 5})
    """
    if result is not None:
        logger.debug(f"<< Exiting {func_name}, result: {result}")
    else:
        logger.debug(f"<< Exiting {func_name}")
