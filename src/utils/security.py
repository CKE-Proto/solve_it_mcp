"""Security utilities for MCP Template.

This module provides essential security functions that should be integrated into
your MCP tools to prevent common security vulnerabilities. These utilities are
currently SCAFFOLDED but NOT AUTOMATICALLY APPLIED - you must explicitly use
them in your tool implementations.

## Critical Security Note

**These utilities are not automatically applied to your tools!**

You must explicitly integrate them into your tool implementations. The template
provides the utilities but doesn't enforce their use to maintain flexibility.

## Security Functions Overview

- `sanitize_input()`: Clean user input to prevent injection attacks
- `sanitize_error()`: Clean error messages to prevent information leakage
- `validate_path()`: Prevent path traversal attacks on file operations
- `RateLimiter`: Prevent abuse through request rate limiting

## Integration Patterns

### Basic Tool Security Pattern
```python
from mcp_template.utils.security import sanitize_input, validate_path, sanitize_error
from mcp_template.utils.logging import get_logger

logger = get_logger(__name__)

class SecureFileTool(BaseTool[FileToolParams]):
    async def invoke(self, params: FileToolParams) -> str:
        try:
            # 1. Sanitize all user inputs
            clean_filename = sanitize_input(params.filename)

            # 2. Validate file paths to prevent traversal attacks
            safe_path = await validate_path(params.file_path)

            # 3. Your business logic here
            result = process_file(safe_path, clean_filename)
            return result

        except Exception as e:
            # 4. Sanitize error messages
            logger.error(f"File operation failed: {e}")
            raise ToolError(sanitize_error(str(e)))
```

### Rate Limiting Pattern
```python
# Global rate limiter (5 requests per second)
rate_limiter = RateLimiter(rate=5, per_seconds=1.0)

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    # Apply rate limiting to all tool calls
    if not await rate_limiter.allow():
        raise ToolError("Rate limit exceeded. Please slow down.")

    # Continue with normal tool processing...
```

## Security Best Practices

1. **Input Sanitization**: Always sanitize user-provided strings
2. **Path Validation**: Never trust file paths from users
3. **Error Sanitization**: Never expose internal details in error messages
4. **Rate Limiting**: Protect against abuse and DoS attacks
5. **Defense in Depth**: Use multiple security layers

## Common Security Mistakes

❌ **DON'T DO THIS:**
```python
# Direct use of user input - DANGEROUS!
async def invoke(self, params: MyParams) -> str:
    with open(params.file_path, 'r') as f:  # Path traversal vulnerability!
        return f.read()
```

✅ **DO THIS INSTEAD:**
```python
# Properly secured version
async def invoke(self, params: MyParams) -> str:
    try:
        safe_path = await validate_path(params.file_path)
        with open(safe_path, 'r') as f:
            return f.read()
    except Exception as e:
        raise ToolError(sanitize_error(str(e)))
```

## Enterprise Considerations

For enterprise deployments, consider implementing:
- **Authentication**: Verify client identity before processing
- **Authorization**: Control which tools clients can access
- **Data Masking**: Redact sensitive information from responses
- **Audit Logging**: Track all security-relevant events
- **Network Security**: Use HTTPS and secure transport configurations
"""

from __future__ import annotations

import asyncio
import os
import re
from pathlib import Path
from time import monotonic

from .logging import get_logger

logger = get_logger(__name__)


def sanitize_input(input_data: str) -> str:
    """Sanitize user-provided input to prevent injection attacks.

    Removes potentially dangerous characters from user input, keeping only
    alphanumeric characters, whitespace, hyphens, underscores, and periods.

    **Security Purpose**: Prevents various injection attacks including:
    - Command injection (removes shell metacharacters)
    - Path injection (removes path separators)
    - Script injection (removes HTML/JavaScript special chars)

    Args:
        input_data: Raw user input string to sanitize.

    Returns:
        Sanitized string with dangerous characters removed.

    Example:
        ```python
        user_input = "file<script>alert(1)</script>.txt"
        safe_input = sanitize_input(user_input)
        # Result: "filescriptalert1scripttxt"
        ```

    Note:
        This is a conservative approach that may remove legitimate characters.
        For more nuanced sanitization, implement custom validation in your
        tool's parameter model using Pydantic validators.
    """
    return re.sub(r"[^\w\s\-_.]", "", input_data)


def sanitize_error(error: str) -> str:
    """Sanitize error messages to prevent information leakage.

    Cleans error messages to remove potentially sensitive information
    while preserving basic error details for debugging.

    **Security Purpose**: Prevents accidental disclosure of:
    - File paths and system structure
    - Database connection strings
    - Internal service details
    - Stack traces with sensitive info

    Args:
        error: Raw error message string.

    Returns:
        Sanitized error message, truncated to 200 characters max.

    Example:
        ```python
        raw_error = "Failed to connect to database at /secret/path/db.sqlite"
        safe_error = sanitize_error(raw_error)
        # Result: "Failed to connect to database at secretpathdbsqlite"
        ```

    Note:
        For production systems, consider implementing structured logging
        where sensitive details are logged internally but not returned
        to clients.
    """
    sanitized = re.sub(r"[^a-zA-Z0-9 .:_-]", "", error)
    return sanitized[:200]


async def validate_path(path: str) -> str:
    """Validate filesystem path to prevent directory traversal attacks.

    Checks for path traversal attempts (../) and resolves the path to
    its absolute form to prevent access to unauthorized directories.

    **Security Purpose**: Prevents directory traversal attacks where
    malicious users try to access files outside the intended directory
    using relative paths like "../../../etc/passwd".

    Args:
        path: File path string to validate.

    Returns:
        Absolute path string if validation passes.

    Raises:
        ValueError: If path contains traversal attempts (..).

    Example:
        ```python
        # Safe path
        safe_path = await validate_path("data/file.txt")
        # Result: "/app/data/file.txt" (absolute path)

        # Dangerous path - raises ValueError
        try:
            bad_path = await validate_path("../../../etc/passwd")
        except ValueError:
            print("Path traversal attempt blocked!")
        ```

    Security Note:
        This function only validates the path structure. You should also:
        1. Check if the resolved path is within your allowed directories
        2. Verify file permissions before access
        3. Implement additional application-specific path restrictions
    """
    candidate = Path(path)
    resolved = candidate.resolve()
    if ".." in candidate.parts:
        raise ValueError("Invalid path")
    return str(resolved)


class RateLimiter:
    """Token bucket rate limiter for preventing abuse and DoS attacks.

    Implements a token bucket algorithm to limit the rate of requests.
    Tokens are added to the bucket at a constant rate, and each request
    consumes one token. When the bucket is empty, requests are denied.

    **Security Purpose**: Protects against:
    - Denial of Service (DoS) attacks
    - API abuse and resource exhaustion
    - Brute force attacks
    - Excessive automated requests

    The token bucket algorithm allows for bursts of requests up to the
    bucket capacity while maintaining an average rate limit over time.

    Example:
        ```python
        # Allow 10 requests per minute
        limiter = RateLimiter(rate=10, per_seconds=60.0)

        # In your request handler
        if await limiter.allow():
            # Process request
            return handle_request()
        else:
            # Reject request
            raise ToolError("Rate limit exceeded")
        ```

    Thread Safety:
        This class is async-safe and can be used concurrently across
        multiple requests using asyncio locks.
    """

    def __init__(self, rate: int, per_seconds: float) -> None:
        """Initialize the rate limiter.

        Args:
            rate: Maximum number of requests allowed in the time window.
            per_seconds: Time window in seconds for the rate limit.

        Example:
            ```python
            # 5 requests per second
            limiter = RateLimiter(rate=5, per_seconds=1.0)

            # 100 requests per hour
            limiter = RateLimiter(rate=100, per_seconds=3600.0)
            ```
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.allowance: float = float(rate)
        self.last_check = monotonic()
        self._lock = asyncio.Lock()

    async def allow(self) -> bool:
        """Check if a request should be allowed based on rate limits.

        This method implements the token bucket algorithm:
        1. Calculate tokens to add based on time elapsed
        2. Add tokens to bucket (up to maximum capacity)
        3. If bucket has tokens, consume one and allow request
        4. If bucket is empty, deny request

        Returns:
            True if request should be allowed, False if rate limit exceeded.

        Example:
            ```python
            if await rate_limiter.allow():
                # Process the request
                result = await process_request()
                return result
            else:
                # Rate limit exceeded
                raise ToolError("Too many requests")
            ```

        Note:
            This method is thread-safe and can be called concurrently
            from multiple async tasks.
        """
        async with self._lock:
            current = monotonic()
            time_passed = current - self.last_check
            self.last_check = current
            self.allowance += time_passed * (self.rate / self.per_seconds)
            if self.allowance > self.rate:
                self.allowance = self.rate
            if self.allowance < 1.0:
                return False
            self.allowance -= 1.0
            return True


def validate_tool_security_config(tool: 'BaseTool') -> None:
    """Validate tool security configuration at registration time.
    
    This function ensures that tools have valid security configurations
    and helps catch configuration errors early in the development process.
    
    Args:
        tool: BaseTool instance to validate.
        
    Raises:
        SecurityConfigError: If tool security configuration is invalid.
    """
    from .shared_security import get_shared_security_config
    
    # Get shared security configuration
    config = get_shared_security_config()
    
    # Validate execution timeout configuration
    if hasattr(tool, 'execution_timeout'):
        timeout = tool.execution_timeout
        
        if timeout > config.max_timeout:
            raise SecurityConfigError(
                f"Tool '{tool.name}' timeout ({timeout}s) exceeds maximum ({config.max_timeout}s). "
                f"Reduce timeout or increase MCP_MAX_TIMEOUT environment variable."
            )
        
        if timeout > 60.0 and not getattr(tool, 'allow_long_execution', False):
            raise SecurityConfigError(
                f"Tool '{tool.name}' requests {timeout}s timeout but allow_long_execution=False. "
                f"Set allow_long_execution=True to explicitly allow timeouts > 60s."
            )
    
    # Validate path validation configuration
    if getattr(tool, 'require_path_validation', False):
        allowed_paths = getattr(tool, 'allowed_paths', [])
        if not allowed_paths:
            raise SecurityConfigError(
                f"Tool '{tool.name}' requires path validation but no allowed_paths defined. "
                f"Define allowed_paths list with permitted directory paths."
            )
        
        # Validate that allowed paths are absolute and exist
        for path in allowed_paths:
            if not os.path.isabs(path):
                raise SecurityConfigError(
                    f"Tool '{tool.name}' allowed_path '{path}' must be absolute path."
                )
    
    # Check for file path parameters without path validation
    if hasattr(tool, 'Params'):
        param_model = tool.Params
        if hasattr(param_model, 'model_fields'):
            for field_name, field_info in param_model.model_fields.items():
                # Check if field name suggests file path handling
                if any(keyword in field_name.lower() for keyword in ['path', 'file', 'dir', 'folder']):
                    if not getattr(tool, 'require_path_validation', False):
                        logger.warning(
                            f"Tool '{tool.name}' has parameter '{field_name}' that may handle file paths "
                            f"but path validation is disabled. Consider setting require_path_validation=True."
                        )


class SecurityConfigError(Exception):
    """Raised when tool security configuration is invalid."""


__all__ = [
    "sanitize_input", 
    "sanitize_error", 
    "validate_path", 
    "RateLimiter",
    "validate_tool_security_config",
    "SecurityConfigError"
]
