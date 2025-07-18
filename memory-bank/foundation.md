# Foundation - Core Project Knowledge

## Project Vision
**Production-ready, forkable MCP server template** using the official MCP SDK. Enables developers to build custom MCP servers in <10 minutes while maintaining code quality, security, and maintainability.

**Design Philosophy**: "SDK-First Simplicity"
- Leverage official MCP SDK for all protocol handling
- Focus template value on tool development patterns only
- Convention over configuration with sensible defaults
- Examples with documentation - working code teaches
- Fork-first design optimized for copying and customization

## Core Architecture (SDK-Based)

### Component Structure
```
Official MCP SDK Server
├── Tool Registration (via decorators)
│   └── BaseTool[T] instances (our value-add)
└── SDK handles all protocol/transport complexity
```

### Data Flow
```
Client Request → SDK → Tool Handlers → BaseTool[T] → SDK → Client Response
```

## Essential Patterns

### Tool Development Pattern
```python
from pydantic import Field, field_validator
from mcp_template.tools.base import BaseTool, ToolParams

class MyToolParams(ToolParams):
    operation: str = Field(description="Operation to perform")
    value: int = Field(description="Input value")
    
    @field_validator("operation")
    @classmethod
    def validate_operation(cls, v: str) -> str:
        valid_ops = ["process", "transform"]
        if v not in valid_ops:
            raise ValueError(f"Invalid operation '{v}'. Must be one of: {', '.join(valid_ops)}")
        return v

class MyTool(BaseTool[MyToolParams]):
    name = "my_tool"
    description = "Example tool that processes values"
    Params = MyToolParams
    
    async def invoke(self, params: MyToolParams) -> str:
        # Auto-injected logger available immediately
        self.logger.info(f"Performing {params.operation} on value: {params.value}")
        
        if params.operation == "process":
            result = params.value * 2
            self.logger.debug(f"Processing result: {result}")
            return f"Processed: {params.value} → {result}"
        elif params.operation == "transform":
            result = params.value + 10
            self.logger.debug(f"Transform result: {result}")
            return f"Transformed: {params.value} → {result}"

# Tool registration with SDK server
my_tool = MyTool()

# In server.py - tools are registered in a registry
tools = [MyTool(), CalculatorTool()]
tool_registry = {tool.name: tool for tool in tools}

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
    if name not in tool_registry:
        raise ValueError(f"Unknown tool: {name}")
    
    tool = tool_registry[name]
    params = tool.validate_params(arguments or {})
    result = await tool.invoke(params)
    return [types.TextContent(type="text", text=str(result))]
```

### Error Handling Strategy
- Tools: Raise specific exceptions
- SDK: Handles all protocol-level error responses automatically
- No custom error mapping needed

### Parameter Validation & Auto-Injection Logging (Our Value-Add)
- Dictionary → Pydantic Model → Validated Parameters
- Automatic schema generation for MCP protocol
- Runtime validation with helpful error messages
- Auto-injected standardized logger (`self.logger`) in all tools
- Logger inherits production configuration (JSON format, correlation IDs, etc.)

## Technology Stack

### Core Dependencies
```toml
dependencies = [
    "mcp>=1.0.0",
    "pydantic>=2.0,<3.0",
    "aiofiles>=23.0",
    "httpx>=0.25,<1.0",
    "anyio>=4.0,<5.0",
]
```

### Development Standards
- **Python**: 3.11+ (modern async features, better type hints)
- **Type Safety**: 100% type coverage with mypy strict mode
- **Validation**: Pydantic V2 for all data models
- **Testing**: pytest with asyncio support, >90% coverage target
- **Code Quality**: ruff for linting/formatting, mypy for type checking

## Security Architecture: "Security by Default, Flexibility by Choice"

### Layer 1: Automatic Server-Level Protections (Cannot be bypassed)
- **Global Rate Limiting**: 100 requests/minute default (configurable via MCP_RATE_LIMIT)
- **Input Size Limits**: 1MB default (configurable via MCP_MAX_INPUT_SIZE)
- **Output Size Limits**: 10MB default (configurable via MCP_MAX_OUTPUT_SIZE)
- **Execution Timeouts**: 30s default, 5min max (configurable via MCP_DEFAULT_TIMEOUT/MCP_MAX_TIMEOUT)
- **Output Rate Limiting**: 50MB/minute (configurable via MCP_OUTPUT_RATE_LIMIT)
- **Type Safety Validation**: Blocks dangerous objects like functions
- **String Length Validation**: 100KB per string (configurable via MCP_MAX_STRING_LENGTH)

### Layer 2: Tool-Level Security Configuration (Guided defaults)
- **Auto-Sanitize Strings**: Default ON, removes dangerous characters
- **Path Validation**: Opt-in for file operations with directory whitelisting
- **Tool-Specific Timeouts**: Custom timeouts with validation
- **Security Configuration Validation**: Automatic validation at tool initialization
- **Developer Warnings**: Automatic warnings for potential security issues

### Layer 3: Explicit Developer Choices (Conscious security decisions)
- **Path Whitelisting**: Must define allowed directories for file operations
- **Custom Timeout Acknowledgment**: Must explicitly allow timeouts >60s
- **Security Feature Overrides**: Clear documentation requirements

### Security Implementation
- **SecurityMiddleware**: Automatic Layer 1 enforcement in `utils/security_middleware.py`
- **Enhanced BaseTool**: Layer 2 security integration with configuration validation
- **Security Utilities**: Path validation, input sanitization in `utils/security.py`
- **Comprehensive Testing**: 19 security tests covering protections noted above.

## Non-Negotiable Constraints
- **SDK-First**: Use official MCP SDK for ALL protocol handling
- **Single BaseTool Definition**: Only `tools/base.py` version (eliminates confusion)
- **Type-Safe Throughout**: All public APIs must have complete type hints
- **Tool-Focused**: Template only adds value around tool patterns, nothing else

## 📁 File Structure (Simplified)
```
mcp_template/
├── server.py               # SDK-based server (main entry point)
├── tools/
│   ├── base.py            # BaseTool[T] pattern (our value-add)
│   └── examples/          # Example tools
├── utils/                 # Security, logging utilities
├── examples/              # Usage examples
└── tests/                 # Test suite
```

## 🔌 Extension Points
- **Custom Tool Types**: Extend `BaseTool[T]` for specialized behavior
- **Tool Middleware**: Add validation/logging around tool calls
- **Security Utilities**: Path validation, input sanitization (scaffolded)
- **Auto-Injection Logging**: Standardized logger automatically available in all tools

## Success Targets (Revised)
- **Time to first custom tool**: <10 minutes ✅
- **Time to forked server**: <5 minutes (just copy server.py + add tools)
- **Basic server setup**: <30 lines of code (SDK does the heavy lifting)
- **Example tools available**: 2 working examples (AsyncEcho, Calculator) ✅
- **Auto-injection logging**: Zero-boilerplate logger setup ✅
- **Test coverage**: >90%
- **Type coverage**: 100%
- **MCP Protocol**: Fully handled by SDK ✅

## Development Process
1. **Tool Development**: Follow BaseTool[T] pattern with type-safe parameters
2. **Registration**: Simple decorator-based registration with SDK server
3. **Testing**: Focus on tool logic, not protocol compliance
4. **Security**: Path validation and input sanitization by default
5. **Deployment**: SDK handles all transport and protocol complexity

## Key Value Propositions
1. **Tool Pattern**: Clean, type-safe tool development with automatic validation
2. **Auto-Injection Logging**: Zero-boilerplate standardized logging in all tools
3. **Quick Setup**: Fork and deploy in minutes, not hours
4. **Battle-Tested Protocol**: Let Anthropic maintain the MCP implementation
5. **Production-Ready**: Comprehensive logging, error handling, and security scaffolding
6. **Focus**: Template focuses on business logic, not plumbing
