"""Structured logging utilities for MCP Template.

This module provides standardized logging configuration for MCP tools and servers.
The logging is designed to be production-ready with structured output and
appropriate security considerations.

## Why Use This Instead of Standard Logging?

- **Consistent Format**: All logs follow the same structured format
- **Security-Aware**: Designed to work with error sanitization
- **Production-Ready**: Appropriate log levels and formatting for deployment
- **Tool-Specific**: Easy to identify which tool generated which logs

## Basic Usage

```python
from mcp_template.utils.logging import get_logger

logger = get_logger(__name__)  # Use module name as logger name

# In your tool implementation
class MyTool(BaseTool[MyToolParams]):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")

    async def invoke(self, params: MyToolParams) -> str:
        self.logger.info(f"Processing request with param: {params.some_field}")

        try:
            result = await some_operation()
            self.logger.info("Operation completed successfully")
            return result
        except Exception as e:
            # Log the full error internally
            self.logger.error(f"Operation failed: {e}")
            # Return sanitized error to client
            raise ToolError(sanitize_error(str(e)))
```

## Security Integration

When using with security utilities, follow this pattern:

```python
from mcp_template.utils.logging import get_logger
from mcp_template.utils.security import sanitize_error

logger = get_logger(__name__)

try:
    # Your tool logic here
    result = perform_operation()
except Exception as e:
    # Log full error details internally (for debugging)
    logger.error(f"Internal error in {operation_name}: {e}")
    logger.error(f"Full traceback: {traceback.format_exc()}")

    # Return sanitized error to client (for security)
    raise ToolError(sanitize_error(str(e)))
```

## Log Levels Guide

- **DEBUG**: Detailed diagnostic information, typically of interest only when 
  diagnosing problems
- **INFO**: General information about tool execution (default level)
- **WARNING**: Something unexpected happened, but the tool is still working
- **ERROR**: A serious problem occurred; the tool couldn't perform its function
- **CRITICAL**: A very serious error occurred; the server might be unable to continue

## Production Considerations

For production deployments, consider:

1. **Log Aggregation**: Send logs to centralized logging systems
2. **Log Rotation**: Prevent log files from consuming too much disk space
3. **Sensitive Data**: Never log passwords, tokens, or personal information
4. **Performance**: Avoid excessive logging in high-frequency operations
5. **Monitoring**: Set up alerts for ERROR and CRITICAL level logs

## Advanced Configuration

For more advanced logging needs, you can customize the logger:

```python
import logging
from mcp_template.utils.logging import get_logger

# Get the base logger
logger = get_logger(__name__)

# Add additional handlers for specific needs
file_handler = logging.FileHandler('mcp_server.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s'
))
logger.addHandler(file_handler)

# Set different log level for file vs console
logger.handlers[0].setLevel(logging.WARNING)  # Console: warnings and above
file_handler.setLevel(logging.DEBUG)          # File: everything
```
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class LogConfig:
    """Configuration for logging system.

    This configuration is primarily driven by environment variables,
    making it easy to configure logging for different deployment environments
    without code changes.

    Environment Variables:
        LOG_LEVEL: Logging level (DEBUG, INFO, WARN, ERROR, CRITICAL)
        LOG_TO_FILE: Enable file logging (true/false)
        LOG_FILE_PATH: Path for log file (default: ./mcp_server.log)
        LOG_TO_SYSLOG: Enable syslog logging (true/false)
        LOG_SYSLOG_FACILITY: Syslog facility (default: local0)
        LOG_FORMAT: Log format (human/json)
        LOG_CORRELATION_IDS: Enable correlation ID tracking (true/false)

    Examples:
        # Development (default)
        LOG_LEVEL=DEBUG

        # Production with file logging
        LOG_LEVEL=INFO
        LOG_TO_FILE=true
        LOG_FILE_PATH=/var/log/mcp/server.log

        # Production with syslog
        LOG_LEVEL=WARN
        LOG_TO_SYSLOG=true
        LOG_SYSLOG_FACILITY=local1

        # Structured logging for log aggregation
        LOG_FORMAT=json
        LOG_TO_FILE=true
    """

    level: str = "INFO"
    console: bool = True
    file_path: Optional[str] = None
    syslog: bool = False
    syslog_facility: str = "local0"
    format_type: str = "human"  # "human" or "json"
    correlation_ids: bool = True

    @classmethod
    def from_env(cls) -> "LogConfig":
        """Create LogConfig from environment variables.

        This method reads configuration from environment variables,
        providing sensible defaults for all settings.

        Returns:
            LogConfig instance configured from environment.
        """
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO").upper(),
            console=True,  # Always enabled, but can be customized via code
            file_path=os.getenv("LOG_FILE_PATH") if _env_bool("LOG_TO_FILE") else None,
            syslog=_env_bool("LOG_TO_SYSLOG", False),
            syslog_facility=os.getenv("LOG_SYSLOG_FACILITY", "local0"),
            format_type=os.getenv("LOG_FORMAT", "human").lower(),
            correlation_ids=_env_bool("LOG_CORRELATION_IDS", True),
        )


def _env_bool(key: str, default: bool = False) -> bool:
    """Convert environment variable to boolean.

    Accepts: true, false, 1, 0, yes, no (case insensitive)

    Args:
        key: Environment variable name.
        default: Default value if not set.

    Returns:
        Boolean value.
    """
    value = os.getenv(key, "").lower()
    if value in ("true", "1", "yes"):
        return True
    elif value in ("false", "0", "no"):
        return False
    return default


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs logs in JSON format suitable for log aggregation systems
    like ELK stack, Splunk, or cloud logging services.

    Output format:
    {
        "timestamp": "2023-12-07T10:30:45.123Z",
        "level": "INFO",
        "logger": "mcp_template.server",
        "message": "Server started",
        "correlation_id": "req_123456",
        "extra_field": "value"
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON formatted log string.
        """
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id

        # Add any extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "correlation_id",
            ):
                log_entry[key] = value

        return json.dumps(log_entry)


def _get_syslog_facility(facility_name: str) -> int:
    """Convert facility name to syslog facility constant.

    Args:
        facility_name: Facility name (e.g., 'local0', 'mail', 'daemon').

    Returns:
        Syslog facility constant.

    Raises:
        ValueError: If facility name is not recognized.
    """
    facilities = {
        "kern": logging.handlers.SysLogHandler.LOG_KERN,
        "user": logging.handlers.SysLogHandler.LOG_USER,
        "mail": logging.handlers.SysLogHandler.LOG_MAIL,
        "daemon": logging.handlers.SysLogHandler.LOG_DAEMON,
        "auth": logging.handlers.SysLogHandler.LOG_AUTH,
        "syslog": logging.handlers.SysLogHandler.LOG_SYSLOG,
        "lpr": logging.handlers.SysLogHandler.LOG_LPR,
        "news": logging.handlers.SysLogHandler.LOG_NEWS,
        "uucp": logging.handlers.SysLogHandler.LOG_UUCP,
        "cron": logging.handlers.SysLogHandler.LOG_CRON,
        "authpriv": logging.handlers.SysLogHandler.LOG_AUTHPRIV,
        "ftp": logging.handlers.SysLogHandler.LOG_FTP,
        "local0": logging.handlers.SysLogHandler.LOG_LOCAL0,
        "local1": logging.handlers.SysLogHandler.LOG_LOCAL1,
        "local2": logging.handlers.SysLogHandler.LOG_LOCAL2,
        "local3": logging.handlers.SysLogHandler.LOG_LOCAL3,
        "local4": logging.handlers.SysLogHandler.LOG_LOCAL4,
        "local5": logging.handlers.SysLogHandler.LOG_LOCAL5,
        "local6": logging.handlers.SysLogHandler.LOG_LOCAL6,
        "local7": logging.handlers.SysLogHandler.LOG_LOCAL7,
    }

    facility_name = facility_name.lower()
    if facility_name not in facilities:
        raise ValueError(f"Unknown syslog facility: {facility_name}")

    return facilities[facility_name]


def configure_logging(config: Optional[LogConfig] = None) -> None:
    """Configure the root logger with multiple handlers.

    This function sets up logging according to the provided configuration,
    adding appropriate handlers for console, file, and syslog output.

    Args:
        config: Logging configuration. If None, loads from environment.

    Note:
        This function should typically be called once at application startup.
        Subsequent calls will reconfigure logging, which may cause issues
        with existing loggers.
    """
    if config is None:
        config = LogConfig.from_env()

    # Get root logger and clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, config.level))

    # Create formatters
    if config.format_type == "json":
        formatter: logging.Formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    # Console handler (stderr)
    if config.console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler
    if config.file_path:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(config.file_path), exist_ok=True)
            file_handler = logging.FileHandler(config.file_path)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except (OSError, IOError) as e:
            # Log to console if file logging fails
            print(
                f"Warning: Could not setup file logging to {config.file_path}: {e}",
                file=sys.stderr,
            )

    # Syslog handler
    if config.syslog:
        try:
            facility = _get_syslog_facility(config.syslog_facility)
            syslog_handler = logging.handlers.SysLogHandler(
                address="/dev/log" if sys.platform != "darwin" else "/var/run/syslog",
                facility=facility,
            )
            syslog_handler.setFormatter(formatter)
            root_logger.addHandler(syslog_handler)
        except (OSError, ValueError) as e:
            # Log to console if syslog fails
            print(f"Warning: Could not setup syslog logging: {e}", file=sys.stderr)


def get_logger(name: str, config: Optional[LogConfig] = None) -> logging.Logger:
    """Get a logger configured for MCP Template with structured output.

    Creates a logger with consistent formatting and appropriate defaults
    for MCP server applications. This function now integrates with the
    enhanced configuration system for production deployments.

    Args:
        name: Logger name, typically __name__ of the calling module.
              This helps identify which component generated each log message.
        config: Optional logging configuration. If None, uses environment
                variables via LogConfig.from_env(). For backward compatibility,
                falls back to simple console logging if configuration fails.

    Returns:
        Configured logger instance ready for use.

    Example:
        ```python
        # Basic usage (backward compatible)
        from mcp_template.utils.logging import get_logger

        logger = get_logger(__name__)

        # Advanced usage with custom config
        from mcp_template.utils.logging import get_logger, LogConfig

        config = LogConfig(level="DEBUG", file_path="./debug.log")
        logger = get_logger(__name__, config)

        # In tool methods
        logger.info("Tool started")
        logger.warning("Unusual condition detected")
        logger.error("Operation failed")
        ```

    Log Format:
        Default format: `2023-12-07T10:30:45 module.name INFO Your message here`
        JSON format (if configured): `{"timestamp": "...", "level": "INFO", ...}`

    Configuration:
        The logger respects the global logging configuration. If configure_logging()
        has been called, this function returns a logger that uses those settings.
        Otherwise, it falls back to simple console logging for backward compatibility.
    """
    logger = logging.getLogger(name)

    # Check if root logger has been configured (handlers exist)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # Global logging is configured, return logger that inherits from root
        return logger

    # Fallback: Configure this specific logger if no global config exists
    # This maintains backward compatibility with existing code
    if not logger.handlers:
        try:
            # Try to use environment configuration
            if config is None:
                config = LogConfig.from_env()

            # Apply basic configuration for this logger only
            handler = logging.StreamHandler(sys.stderr)

            if config.format_type == "json":
                formatter: logging.Formatter = StructuredFormatter()
            else:
                formatter = logging.Formatter(
                    fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S",
                )

            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, config.level, logging.INFO))

        except Exception:
            # Ultimate fallback: simple console logging
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt="%(asctime)s %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

    return logger


__all__ = ["get_logger", "configure_logging", "LogConfig", "StructuredFormatter"]
