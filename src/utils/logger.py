"""
Lightweight picologging configuration for Symbiote.
Usage:
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Hello, world!")
"""

import os
import sys
import picologging as logging
from picologging import StreamHandler, Formatter

# Cache for loggers to avoid recreation overhead
_loggers: dict[str, logging.Logger] = {}

# Default log level from environment, fallback to INFO
_DEFAULT_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_LOG_LEVEL = getattr(logging, _DEFAULT_LEVEL, logging.INFO)

# Minimal, fast format - no datetime parsing overhead in simple mode
_FORMAT = "%(levelname)s | %(name)s | %(message)s"
_DEBUG_FORMAT = "%(levelname)s | %(name)s:%(lineno)d | %(message)s"

# Single shared handler for all loggers (memory efficient)
_handler: StreamHandler | None = None


def _get_handler() -> StreamHandler:
    """Get or create the shared stream handler."""
    global _handler
    if _handler is None:
        _handler = StreamHandler(sys.stderr)
        fmt = _DEBUG_FORMAT if _LOG_LEVEL == logging.DEBUG else _FORMAT
        _handler.setFormatter(Formatter(fmt))
        _handler.setLevel(_LOG_LEVEL)
    return _handler


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance by name.
    
    Loggers are cached for performance - calling this multiple times
    with the same name returns the same logger instance.
    
    Args:
        name: Logger name, typically __name__ of the calling module.
        
    Returns:
        Configured picologging Logger instance.
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(_LOG_LEVEL)
    logger.addHandler(_get_handler())
    
    _loggers[name] = logger
    return logger


def set_level(level: int | str) -> None:
    """
    Dynamically change the log level for all loggers.
    
    Args:
        level: Log level as int (e.g., logging.DEBUG) or string (e.g., "DEBUG").
    """
    global _LOG_LEVEL
    
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    _LOG_LEVEL = level
    
    if _handler:
        _handler.setLevel(level)
    
    for logger in _loggers.values():
        logger.setLevel(level)

