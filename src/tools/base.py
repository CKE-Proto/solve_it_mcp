"""Base classes and patterns for MCP tool implementations.

This module provides the core BaseTool[T] pattern that makes this template valuable.
The pattern provides type-safe, validated, and self-documenting tools that integrate
seamlessly with the MCP SDK.

## Core Design Philosophy

The BaseTool[T] pattern enforces three critical principles:

1. **Type Safety**: Every tool has a strongly-typed parameter model
2. **Automatic Validation**: Parameters are validated at runtime via Pydantic
3. **Self-Documentation**: Tools generate their own JSON schemas for MCP protocol

## Quick Start Example

```python
from pydantic import Field
from mcp_template.tools.base import BaseTool, ToolParams

class MyToolParams(ToolParams):
    message: str = Field(description="The message to process")
    count: int = Field(default=1, description="Number of times to repeat")

class MyTool(BaseTool[MyToolParams]):
    name = "my_tool"
    description = "Example tool that processes messages"
    Params = MyToolParams

    async def invoke(self, params: MyToolParams) -> str:
        return params.message * params.count

# Register with MCP SDK server
my_tool = MyTool()

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    if name == my_tool.name:
        params = my_tool.validate_params(arguments or {})
        result = await my_tool.invoke(params)
        return [types.TextContent(type="text", text=str(result))]
```

## Extension Patterns

### Adding Validation
```python
class MyParams(ToolParams):
    file_path: str = Field(description="Path to file")

    @field_validator("file_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        # Add custom validation logic
        if not v.endswith('.txt'):
            raise ValueError("Only .txt files allowed")
        return v
```

### Error Handling with Auto-Injected Logger
```python
async def invoke(self, params: MyParams) -> str:
    self.logger.info(f"Starting operation for: {params.some_field}")

    try:
        # Your tool logic here
        result = perform_operation()
        self.logger.info("Operation completed successfully")
        return result
    except FileNotFoundError as e:
        self.logger.warning(f"File not found: {e}")
        raise ToolError("File not found")  # Clean error for MCP protocol
    except Exception as e:
        # Log internally with full details, return sanitized error
        self.logger.error(f"Unexpected error: {e}")
        raise ToolError("Internal error occurred")
```

### Security Integration
```python
from mcp_template.utils.security import validate_path, sanitize_input

async def invoke(self, params: MyParams) -> str:
    # Validate file paths to prevent traversal attacks
    safe_path = await validate_path(params.file_path)

    # Sanitize user input
    clean_input = sanitize_input(params.user_text)

    # Proceed with safe values
    return f"Processed: {clean_input}"
```

## Architecture Notes

The BaseTool[T] pattern is designed to:

- **Minimize boilerplate**: Focus on business logic, not parameter handling
- **Maximize safety**: Catch errors at validation time, not runtime
- **Integrate seamlessly**: Works perfectly with MCP SDK decorators
- **Enable composition**: Tools can be combined and extended easily

The generic type parameter `T` ensures your `invoke` method receives exactly
the parameter type you define, with full IDE support and type checking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel

from utils.errors import ToolError
from utils.logging import get_logger
from utils.security import sanitize_input, validate_tool_security_config, SecurityConfigError


class ToolParams(BaseModel):
    """Base class for tool parameter models.

    All tool parameter classes should inherit from this base class.
    This provides the foundation for Pydantic validation and JSON schema generation.

    Example:
        ```python
        class MyToolParams(ToolParams):
            name: str = Field(description="The name to process")
            count: int = Field(default=1, ge=1, description="Number of repetitions")
        ```

    The parameter model serves multiple purposes:
    - **Runtime validation**: Ensures parameters match expected types and constraints
    - **Schema generation**: Automatically creates MCP-compatible JSON schemas
    - **Documentation**: Field descriptions become part of the tool's API docs
    - **Type safety**: Provides full type hints for tool implementation
    """


P = TypeVar("P", bound=ToolParams)


class BaseTool(Generic[P], ABC):
    """Abstract base class for all MCP tools.

    This is the core pattern that makes this template valuable. It provides:

    1. **Type-safe parameter handling** via generic type parameter `P`
    2. **Automatic validation** through Pydantic models
    3. **Schema generation** for MCP protocol compliance
    4. **Consistent error handling** patterns
    5. **Layer 2 security integration** with configurable protections

    ## Required Attributes

    Every tool implementation must define:

    - `name`: Unique identifier for the tool (used in MCP calls)
    - `description`: Human-readable description (shown to LLMs)
    - `Params`: Parameter model class (defines tool's input schema)

    ## Security Configuration (Layer 2)

    Optional security attributes that can be overridden:

    - `execution_timeout`: Maximum execution time in seconds (default: 30s)
    - `allow_long_execution`: Allow timeouts > 60s (default: False)
    - `auto_sanitize_strings`: Automatically sanitize string inputs (default: True)
    - `require_path_validation`: Require path validation for file operations (default: False)
    - `allowed_paths`: List of allowed directory paths (required if require_path_validation=True)

    ## Implementation Pattern

    ```python
    class MyTool(BaseTool[MyToolParams]):
        name = "my_tool"                    # Tool identifier
        description = "What this tool does" # Tool description
        Params = MyToolParams              # Parameter model
        
        # Security configuration (Layer 2)
        execution_timeout = 45.0           # Custom timeout
        auto_sanitize_strings = True       # Safe default
        require_path_validation = False    # Explicit choice

        async def invoke(self, params: MyToolParams) -> str:
            # Tool implementation here
            return f"Result: {params.some_field}"
    ```

    ## Security Integration Example

    ```python
    class FileProcessingTool(BaseTool[FileParams]):
        name = "file_processor"
        description = "Process files safely"
        Params = FileParams
        
        # Layer 2 security configuration
        execution_timeout = 60.0           # File operations may take longer
        allow_long_execution = True        # Explicit acknowledgment
        require_path_validation = True     # Must validate file paths
        allowed_paths = ["/app/data", "/tmp"]  # Whitelist directories
        
        async def invoke(self, params: FileParams) -> str:
            # Path validation is automatically applied
            # String sanitization is automatically applied
            return self.process_file(params.file_path)
    ```

    ## Parameter Validation Flow

    1. MCP SDK receives raw dictionary parameters
    2. `validate_params()` applies Layer 2 security (sanitization, validation)
    3. Pydantic validates types, constraints, and required fields
    4. `invoke()` receives fully validated and secured parameter object
    5. Type system ensures parameter access is safe

    ## Error Handling Strategy

    - **Validation errors**: Automatically handled by Pydantic
    - **Security errors**: Logged and converted to safe error messages
    - **Business logic errors**: Raise `ToolError` for clean MCP responses
    - **Unexpected errors**: Catch and convert to `ToolError` to avoid leaking details

    ## Integration with MCP SDK

    ```python
    my_tool = MyTool()

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[types.TextContent]:
        if name == my_tool.name:
            # Layer 2 security + validation happens here
            params = my_tool.validate_params(arguments or {})
            # Type-safe invocation
            result = await my_tool.invoke(params)
            return [types.TextContent(type="text", text=str(result))]
    ```

    This pattern ensures tools are self-contained, type-safe, secure, and easily testable.
    """

    # Required attributes
    name: str
    description: str
    params_model: Type[P]
    
    # Layer 2 Security Configuration (with safe defaults)
    execution_timeout: float = 30.0        # Default 30 second timeout
    allow_long_execution: bool = False     # Must opt-in for longer timeouts
    auto_sanitize_strings: bool = True     # Sanitize strings by default
    require_path_validation: bool = False  # Opt-in for file operations
    allowed_paths: list[str] = []          # Must define if path validation enabled

    def __init__(self) -> None:
        """Initialize tool and validate class definition.

        Automatically injects a standardized logger for consistent logging
        across all tools without requiring manual setup. Also validates
        Layer 2 security configuration.

        Raises:
            ValueError: If required class attributes are missing or invalid.
            SecurityConfigError: If security configuration is invalid.
        """
        if not hasattr(self, "name") or not isinstance(self.name, str):
            raise ValueError("Tool must define a 'name' class attribute as a string")
        if not hasattr(self, "description") or not isinstance(self.description, str):
            raise ValueError(
                "Tool must define a 'description' class attribute as a string"
            )
        if not hasattr(self, "Params"):
            raise ValueError(
                "Tool must define a 'Params' class attribute (parameter model)"
            )
        self.params_model = getattr(self, "Params")

        # Auto-inject standardized logger
        logger_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        self.logger = get_logger(logger_name)

        # Validate Layer 2 security configuration
        try:
            validate_tool_security_config(self)
            self.logger.debug(f"Security configuration validated for tool: {self.name}")
        except SecurityConfigError as e:
            self.logger.error(f"Security configuration error for tool {self.name}: {e}")
            raise

        # Log tool initialization
        self.logger.debug(f"Initialized tool: {self.name}")

    def get_schema(self) -> Dict[str, Any]:
        """Return JSON schema for this tool's parameters.

        This schema is used by the MCP protocol to validate parameters
        and provide type information to LLM clients.

        Returns:
            JSON schema dictionary compatible with MCP protocol.
        """
        return self.params_model.model_json_schema()

    def validate_params(self, params: Dict[str, Any]) -> P:
        """Validate and convert parameter dictionary to typed model.

        This is where Layer 2 security features are applied:
        - String sanitization (if auto_sanitize_strings=True)
        - Path validation (if require_path_validation=True)
        - Pydantic validation and type conversion

        Args:
            params: Raw parameter dictionary from MCP call.

        Returns:
            Validated parameter object with full type safety.

        Raises:
            ValidationError: If parameters don't match the schema.
            ToolError: If security validation fails.
        """
        # Apply Layer 2 security features
        secured_params = self._apply_layer2_security(params)
        
        # Standard Pydantic validation
        return self.params_model(**secured_params)
    
    def _apply_layer2_security(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply Layer 2 security features to parameters.
        
        Args:
            params: Raw parameter dictionary.
            
        Returns:
            Security-processed parameter dictionary.
            
        Raises:
            ToolError: If security validation fails.
        """
        if not params:
            return params
        
        # Create a copy to avoid modifying the original
        secured_params = params.copy()
        
        # Apply string sanitization if enabled
        if self.auto_sanitize_strings:
            secured_params = self._sanitize_strings_recursive(secured_params)
            self.logger.debug(f"Applied string sanitization for tool: {self.name}")
        
        # Apply path validation if enabled
        if self.require_path_validation:
            self._validate_paths_in_params(secured_params)
            self.logger.debug(f"Applied path validation for tool: {self.name}")
        
        return secured_params
    
    def _sanitize_strings_recursive(self, obj: Any, path: str = "") -> Any:
        """Recursively sanitize strings in nested data structures.
        
        Args:
            obj: Object to sanitize (can be nested dict/list).
            path: Current path in object hierarchy for logging.
            
        Returns:
            Object with sanitized strings.
        """
        if isinstance(obj, str):
            original_length = len(obj)
            sanitized = sanitize_input(obj)
            if len(sanitized) != original_length:
                self.logger.debug(
                    f"Sanitized string at {path}: {original_length} -> {len(sanitized)} chars",
                    extra={"tool_name": self.name, "path": path}
                )
            return sanitized
        
        elif isinstance(obj, dict):
            return {
                key: self._sanitize_strings_recursive(value, f"{path}.{key}" if path else key)
                for key, value in obj.items()
            }
        
        elif isinstance(obj, list):
            return [
                self._sanitize_strings_recursive(item, f"{path}[{i}]" if path else f"[{i}]")
                for i, item in enumerate(obj)
            ]
        
        else:
            # Return non-string types unchanged
            return obj
    
    def _validate_paths_in_params(self, params: Dict[str, Any]) -> None:
        """Validate file paths in parameters against allowed paths.
        
        Args:
            params: Parameter dictionary to validate.
            
        Raises:
            ToolError: If path validation fails.
        """
        from utils.security import validate_path
        import asyncio
        from pathlib import Path
        
        # Get parameter model fields to identify path parameters
        if hasattr(self.params_model, 'model_fields'):
            for field_name, field_info in self.params_model.model_fields.items():
                if field_name in params:
                    value = params[field_name]
                    
                    # Check if field name suggests file path handling
                    if any(keyword in field_name.lower() for keyword in ['path', 'file', 'dir', 'folder']):
                        if isinstance(value, str):
                            try:
                                # Validate path structure
                                resolved_path = Path(value).resolve()
                                
                                # Check against allowed paths
                                if self.allowed_paths:
                                    path_allowed = False
                                    for allowed_path in self.allowed_paths:
                                        try:
                                            resolved_path.relative_to(Path(allowed_path).resolve())
                                            path_allowed = True
                                            break
                                        except ValueError:
                                            continue
                                    
                                    if not path_allowed:
                                        self.logger.warning(
                                            f"Path not in allowed directories: {value}",
                                            extra={
                                                "tool_name": self.name,
                                                "field_name": field_name,
                                                "path": value,
                                                "allowed_paths": self.allowed_paths
                                            }
                                        )
                                        raise ToolError(f"Path '{value}' is not in allowed directories")
                                
                                self.logger.debug(
                                    f"Path validation passed for {field_name}: {value}",
                                    extra={"tool_name": self.name, "field_name": field_name}
                                )
                                
                            except Exception as e:
                                self.logger.error(
                                    f"Path validation failed for {field_name}: {e}",
                                    extra={"tool_name": self.name, "field_name": field_name, "path": value}
                                )
                                raise ToolError(f"Invalid path in {field_name}: {str(e)}")

    @abstractmethod
    async def invoke(self, params: P) -> Any:
        """Execute the tool with validated parameters.

        This is where you implement your tool's business logic.
        The parameters are guaranteed to be valid and type-safe.

        Args:
            params: Validated parameter object of type P.

        Returns:
            Tool result (will be converted to string for MCP response).

        Raises:
            ToolError: For expected business logic errors.
            Exception: For unexpected errors (should be caught and converted).
        """


__all__ = ["BaseTool", "ToolParams", "ToolError"]
