"""
Structured logging configuration for AarogyaAgent v2.

Provides two output modes controlled by settings:
  - CONSOLE: Human-readable colored output for development
  - JSON: Machine-parseable structured JSON for production observability

A custom CorrelationIdFilter automatically injects the active request
correlation_id into every log record via contextvars.
"""
import logging
import logging.config
import json
from datetime import datetime, timezone
from typing import Any

from core.context import get_correlation_id


class CorrelationIdFilter(logging.Filter):
    """Injects the request correlation ID into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        setattr(record, "correlation_id", get_correlation_id())
        return True


class JSONFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects for production ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", ""),
        }
        
        # Merge extra fields
        standard_keys = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName",
            "processName", "process", "message", "correlation_id", "taskName"
        }
        for key, value in record.__dict__.items():
            if key not in standard_keys:
                log_entry[key] = value

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, default=str)


CONSOLE_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "[%(correlation_id)s] | %(message)s"
)


def setup_logging(log_level: str = "INFO", format_type: str = "CONSOLE") -> None:
    """Configure application logging based on settings.

    Args:
        log_level: The minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format_type: Either 'CONSOLE' for development or 'JSON' for production.
    """
    handlers: dict[str, dict[str, Any]] = {}

    if format_type == "JSON":
        handlers["default"] = {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
            "filters": ["correlation_id"],
        }
    else:
        handlers["default"] = {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "stream": "ext://sys.stdout",
            "filters": ["correlation_id"],
        }

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": CorrelationIdFilter,
            },
        },
        "formatters": {
            "console": {
                "format": CONSOLE_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "handlers": handlers,
        "root": {
            "level": log_level.upper(),
            "handlers": ["default"],
        },
        "loggers": {
            "uvicorn": {"level": "INFO", "handlers": ["default"], "propagate": False},
            "sqlalchemy.engine": {"level": "WARNING", "handlers": ["default"], "propagate": False},
        },
    }

    logging.config.dictConfig(config)
