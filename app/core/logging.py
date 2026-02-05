"""
Logging configuration for the application.

Provides structured logging with consistent formatting across the application.
"""

import logging
import sys
from pathlib import Path

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Sets up:
    - Log level from configuration
    - Consistent formatting
    - Output to stdout (required for Docker containers)
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            # Output to stdout (Docker best practice)
            logging.StreamHandler(sys.stdout),
            # Also log to file for debugging
            logging.FileHandler(log_dir / "app.log")
        ]
    )
    
    # Set log levels for third-party libraries
    # Prevents excessive logging from dependencies
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={settings.log_level}")
