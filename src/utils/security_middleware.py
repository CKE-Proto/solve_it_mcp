"""Security middleware for MCP server request/response processing.

This module implements Layer 1 security protections that are automatically
applied to all tool requests and cannot be bypassed by tool developers.

## Architecture

The SecurityMiddleware class provides three main protection layers:

1. **Request Validation**: Input size limits, rate limiting, type safety
2. **Execution Control**: Timeout enforcement and cancellation handling  
3. **Response Validation**: Output size limits and rate limiting

## Usage

```python
from mcp_template.utils.security_middleware import SecurityMiddleware, SecurityConfig

# Initialize security middleware
security_config = SecurityConfig()
security = SecurityMiddleware(security_config)

# In your server request handler
async def handle_tool_call(name: str, arguments: dict):
    # Layer 1 protections are automatically applied
    await security.validate_request(name, arguments)
    
    async with security.execution_timeout(tool_timeout):
        result = await tool.invoke(params)
    
    safe_result = await security.validate_response(result)
    return safe_result
```

## Configuration

All limits can be configured via environment variables:
- MCP_MAX_INPUT_SIZE: Maximum input size in bytes (default: 1MB)
- MCP_MAX_OUTPUT_SIZE: Maximum output size in bytes (default: 10MB)  
- MCP_DEFAULT_TIMEOUT: Default tool timeout in seconds (default: 30s)
- MCP_MAX_TIMEOUT: Maximum allowed timeout in seconds (default: 300s)
- MCP_RATE_LIMIT: Requests per minute limit (default: 100)
- MCP_OUTPUT_RATE_LIMIT: Output bytes per minute (default: 50MB)
"""

from __future__ import annotations

import asyncio
import os
import re
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from utils.logging import get_logger

logger = get_logger(__name__)


class SecurityError(Exception):
    """Security-related errors that should be logged and handled specially.
    
    These errors indicate potential security violations or resource abuse
    attempts and should be logged with appropriate severity levels.
    """


class SecurityConfig:
    """Centralized security configuration with environment variable support.
    
    This class consolidates all security-related configuration in one place
    and provides sensible defaults while allowing environment-based overrides
    for different deployment scenarios.
    """
    
    def __init__(self) -> None:
        """Initialize security configuration from environment variables."""
        # Input protection limits
        self.max_input_size = int(os.getenv("MCP_MAX_INPUT_SIZE", "1000000"))  # 1MB
        self.max_string_length = int(os.getenv("MCP_MAX_STRING_LENGTH", "100000"))  # 100KB
        
        # Output protection limits  
        self.max_output_size = int(os.getenv("MCP_MAX_OUTPUT_SIZE", "10000000"))  # 10MB
        self.max_output_lines = int(os.getenv("MCP_MAX_OUTPUT_LINES", "50000"))  # 50K lines
        
        # Execution time limits
        self.default_timeout = float(os.getenv("MCP_DEFAULT_TIMEOUT", "30.0"))  # 30 seconds
        self.max_timeout = float(os.getenv("MCP_MAX_TIMEOUT", "300.0"))  # 5 minutes
        
        # Rate limiting
        self.rate_limit_per_minute = int(os.getenv("MCP_RATE_LIMIT", "100"))  # 100 req/min
        self.output_rate_limit = int(os.getenv("MCP_OUTPUT_RATE_LIMIT", "52428800"))  # 50MB/min
        
        # Log configuration on startup
        logger.info(
            "Security configuration initialized",
            extra={
                "max_input_size": self.max_input_size,
                "max_output_size": self.max_output_size,
                "default_timeout": self.default_timeout,
                "rate_limit_per_minute": self.rate_limit_per_minute,
            }
        )


class RateLimiter:
    """Token bucket rate limiter for preventing abuse and DoS attacks.
    
    This is an enhanced version of the rate limiter from security.py,
    optimized for the middleware use case with better async handling.
    """
    
    def __init__(self, rate: int, per_seconds: float) -> None:
        """Initialize the rate limiter.
        
        Args:
            rate: Maximum number of requests allowed in the time window.
            per_seconds: Time window in seconds for the rate limit.
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.allowance: float = float(rate)
        self.last_check = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def allow(self) -> bool:
        """Check if a request should be allowed based on rate limits.
        
        Returns:
            True if request should be allowed, False if rate limit exceeded.
        """
        async with self._lock:
            current = time.monotonic()
            time_passed = current - self.last_check
            self.last_check = current
            
            # Add tokens based on time passed
            self.allowance += time_passed * (self.rate / self.per_seconds)
            if self.allowance > self.rate:
                self.allowance = self.rate
            
            # Check if we have tokens available
            if self.allowance < 1.0:
                return False
            
            self.allowance -= 1.0
            return True


class OutputRateLimiter:
    """Rate limiter specifically for output data volume.
    
    Prevents tools from overwhelming the server or clients with
    excessive output data over time.
    """
    
    def __init__(self, max_bytes_per_minute: int) -> None:
        """Initialize output rate limiter.
        
        Args:
            max_bytes_per_minute: Maximum bytes allowed per minute.
        """
        self.max_bytes = max_bytes_per_minute
        self.window_start = time.monotonic()
        self.bytes_sent = 0
        self._lock = asyncio.Lock()
    
    async def check_output_rate(self, output_size: int) -> bool:
        """Check if output can be sent without exceeding rate limit.
        
        Args:
            output_size: Size of output in bytes.
            
        Returns:
            True if output is within rate limit, False otherwise.
        """
        async with self._lock:
            now = time.monotonic()
            
            # Reset window if needed (sliding window)
            if now - self.window_start > 60:
                self.window_start = now
                self.bytes_sent = 0
            
            # Check if adding this output would exceed limit
            if self.bytes_sent + output_size > self.max_bytes:
                return False
            
            self.bytes_sent += output_size
            return True


class SecurityMiddleware:
    """Handles all Layer 1 security enforcement for MCP server.
    
    This class implements automatic security protections that cannot be
    bypassed by tool developers. All protections are applied transparently
    at the server level.
    """
    
    def __init__(self, config: SecurityConfig) -> None:
        """Initialize security middleware with configuration.
        
        Args:
            config: Security configuration object.
        """
        self.config = config
        
        # Initialize rate limiters
        self.rate_limiter = RateLimiter(
            config.rate_limit_per_minute, 
            60.0  # per minute
        )
        self.output_limiter = OutputRateLimiter(config.output_rate_limit)
        
        logger.info("Security middleware initialized")
    
    async def validate_request(self, name: str, arguments: Dict[str, Any]) -> None:
        """Layer 1: Request validation - always applied.
        
        Validates incoming requests for security threats including:
        - Rate limiting violations
        - Oversized inputs
        - Dangerous object types
        
        Args:
            name: Tool name being called.
            arguments: Tool arguments dictionary.
            
        Raises:
            SecurityError: If request violates security policies.
        """
        # Rate limiting check
        if not await self.rate_limiter.allow():
            logger.warning(
                f"Rate limit exceeded for tool: {name}",
                extra={"tool_name": name, "security_violation": "rate_limit"}
            )
            raise SecurityError("Rate limit exceeded. Please slow down.")
        
        # Input size validation
        input_str = str(arguments)
        input_size = len(input_str)
        
        if input_size > self.config.max_input_size:
            logger.warning(
                f"Input size limit exceeded: {input_size} bytes",
                extra={
                    "tool_name": name,
                    "input_size": input_size,
                    "limit": self.config.max_input_size,
                    "security_violation": "input_size"
                }
            )
            raise SecurityError(f"Input too large: {input_size} bytes (limit: {self.config.max_input_size})")
        
        # String length validation for individual parameters
        self._validate_string_lengths(arguments, name)
        
        # Type safety validation
        self._validate_safe_types(arguments, name)
        
        logger.debug(
            f"Request validation passed for tool: {name}",
            extra={"tool_name": name, "input_size": input_size}
        )
    
    def _validate_string_lengths(self, obj: Any, tool_name: str, path: str = "") -> None:
        """Recursively validate string lengths in nested data structures.
        
        Args:
            obj: Object to validate (can be nested dict/list).
            tool_name: Name of tool for logging.
            path: Current path in object hierarchy for error reporting.
            
        Raises:
            SecurityError: If any string exceeds maximum length.
        """
        if isinstance(obj, str):
            if len(obj) > self.config.max_string_length:
                logger.warning(
                    f"String length limit exceeded at {path}",
                    extra={
                        "tool_name": tool_name,
                        "string_length": len(obj),
                        "limit": self.config.max_string_length,
                        "path": path,
                        "security_violation": "string_length"
                    }
                )
                raise SecurityError(f"String too long at {path}: {len(obj)} chars (limit: {self.config.max_string_length})")
        
        elif isinstance(obj, dict):
            for key, value in obj.items():
                self._validate_string_lengths(value, tool_name, f"{path}.{key}" if path else key)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._validate_string_lengths(item, tool_name, f"{path}[{i}]" if path else f"[{i}]")
    
    def _validate_safe_types(self, obj: Any, tool_name: str, path: str = "") -> None:
        """Validate that object contains only safe, serializable types.
        
        Args:
            obj: Object to validate.
            tool_name: Name of tool for logging.
            path: Current path in object hierarchy.
            
        Raises:
            SecurityError: If dangerous types are detected.
        """
        # Check for dangerous types
        if callable(obj) or hasattr(obj, '__code__'):
            logger.error(
                f"Dangerous object type detected: {type(obj).__name__}",
                extra={
                    "tool_name": tool_name,
                    "object_type": type(obj).__name__,
                    "path": path,
                    "security_violation": "dangerous_type"
                }
            )
            raise SecurityError(f"Dangerous object type not allowed: {type(obj).__name__}")
        
        # Recursively check nested structures
        if isinstance(obj, dict):
            for key, value in obj.items():
                self._validate_safe_types(value, tool_name, f"{path}.{key}" if path else key)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._validate_safe_types(item, tool_name, f"{path}[{i}]" if path else f"[{i}]")
    
    async def validate_response(self, result: Any, tool_name: str) -> str:
        """Layer 1: Response validation - always applied.
        
        Validates tool responses for security and resource concerns:
        - Output size limits
        - Output rate limiting
        - Line count limits
        
        Args:
            result: Tool result to validate.
            tool_name: Name of tool that generated result.
            
        Returns:
            Validated and potentially truncated result string.
            
        Raises:
            SecurityError: If output rate limits are exceeded.
        """
        result_str = str(result)
        original_size = len(result_str)
        truncated = False
        
        # Output size check with truncation
        if len(result_str) > self.config.max_output_size:
            result_str = result_str[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED - SIZE LIMIT EXCEEDED]"
            truncated = True
            
            logger.warning(
                f"Output truncated due to size limit",
                extra={
                    "tool_name": tool_name,
                    "original_size": original_size,
                    "truncated_size": len(result_str),
                    "limit": self.config.max_output_size,
                    "security_action": "truncate_output"
                }
            )
        
        # Line count check with truncation
        lines = result_str.split('\n')
        if len(lines) > self.config.max_output_lines:
            result_str = '\n'.join(lines[:self.config.max_output_lines]) + "\n[OUTPUT TRUNCATED - LINE LIMIT EXCEEDED]"
            truncated = True
            
            logger.warning(
                f"Output truncated due to line limit",
                extra={
                    "tool_name": tool_name,
                    "original_lines": len(lines),
                    "truncated_lines": self.config.max_output_lines,
                    "security_action": "truncate_lines"
                }
            )
        
        # Output rate limiting check
        final_size = len(result_str)
        if not await self.output_limiter.check_output_rate(final_size):
            logger.error(
                f"Output rate limit exceeded",
                extra={
                    "tool_name": tool_name,
                    "output_size": final_size,
                    "security_violation": "output_rate_limit"
                }
            )
            raise SecurityError("Output rate limit exceeded - server is sending too much data")
        
        # Log successful validation
        if not truncated:
            logger.debug(
                f"Response validation passed for tool: {tool_name}",
                extra={"tool_name": tool_name, "output_size": final_size}
            )
        
        return result_str
    
    @asynccontextmanager
    async def execution_timeout(self, tool_timeout: float, tool_name: str):
        """Layer 1: Execution timeout - always applied.
        
        Provides automatic timeout enforcement for tool execution.
        The effective timeout is the minimum of the requested timeout
        and the configured maximum timeout.
        
        Args:
            tool_timeout: Requested timeout in seconds.
            tool_name: Name of tool for logging.
            
        Raises:
            SecurityError: If execution exceeds timeout.
        """
        effective_timeout = min(tool_timeout, self.config.max_timeout)
        
        if effective_timeout != tool_timeout:
            logger.info(
                f"Tool timeout capped at maximum",
                extra={
                    "tool_name": tool_name,
                    "requested_timeout": tool_timeout,
                    "effective_timeout": effective_timeout,
                    "max_timeout": self.config.max_timeout
                }
            )
        
        try:
            async with asyncio.timeout(effective_timeout):
                yield
        except asyncio.TimeoutError:
            logger.error(
                f"Tool execution timeout",
                extra={
                    "tool_name": tool_name,
                    "timeout_seconds": effective_timeout,
                    "security_violation": "execution_timeout"
                }
            )
            raise SecurityError(f"Tool '{tool_name}' execution timeout ({effective_timeout}s)")


__all__ = ["SecurityMiddleware", "SecurityConfig", "SecurityError"]
