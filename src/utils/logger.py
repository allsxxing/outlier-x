"""Logging configuration for outlier-x."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from src.utils.constants import LOG_LEVELS, DEFAULT_LOG_LEVEL


def setup_logger(
    name: str,
    log_level: str = DEFAULT_LOG_LEVEL,
    log_dir: Optional[str] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    Set up a logger with file and console handlers.

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory for log files (defaults to ./logs)
        console_output: Whether to output to console

    Returns:
        Configured logger instance

    Raises:
        ValueError: If log_level is invalid
    """
    if log_level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_level}. Must be one of {LOG_LEVELS}")

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_path / f"{name}.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # Keep 7 days of logs
        )
        file_handler.setLevel(getattr(logging, log_level))
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
