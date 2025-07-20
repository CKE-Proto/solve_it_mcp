#!/usr/bin/env python3
"""SOLVE-IT MCP Server using the official MCP SDK.

This server provides LLM access to the SOLVE-IT Digital Forensics Knowledge Base
through the Model Context Protocol (MCP). It exposes techniques, weaknesses,
mitigations, and their relationships as type-safe MCP tools.

Features:
- Comprehensive SOLVE-IT knowledge base access
- Type-safe parameter validation
- Configurable data path
- Production-ready logging and error handling
- Multi-layer security architecture
"""

import argparse
import asyncio
import os
import sys
import time
import uuid
from typing import Any, Dict

import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from tools.base import BaseTool
from tools.solveit_tools import (
    GetDatabaseDescriptionTool,
    SearchTool,
    GetTechniqueDetailsTool,
    GetWeaknessDetailsTool,
    GetMitigationDetailsTool,
    GetWeaknessesForTechniqueTool,
    GetMitigationsForWeaknessTool,
    # Reverse Relationships
    GetTechniquesForWeaknessTool,
    GetWeaknessesForMitigationTool,
    GetTechniquesForMitigationTool,
    # Objective/Mapping Management
    ListObjectivesTool,
    GetTechniquesForObjectiveTool,
    ListAvailableMappingsTool,
    LoadObjectiveMappingTool,
    # Bulk Retrieval - Concise Format
    GetAllTechniquesWithNameAndIdTool,
    GetAllWeaknessesWithNameAndIdTool,
    GetAllMitigationsWithNameAndIdTool,
    # Bulk Retrieval - Full Detail Format
    GetAllTechniquesWithFullDetailTool,
    GetAllWeaknessesWithFullDetailTool,
    GetAllMitigationsWithFullDetailTool,
)
from utils.logging import configure_logging, get_logger
from utils.security_middleware import SecurityMiddleware, SecurityError
from utils.shared_security import SharedSecurityConfig
from utils.knowledge_base_manager import SharedKnowledgeBase


async def run_stdio_server(server: Server) -> None:
    """Run server with STDIO transport (current default).
    
    This function encapsulates the STDIO transport logic to enable future
    transport abstraction without breaking existing integrations.
    
    Args:
        server: Configured MCP server instance ready to run
    """
    logger = get_logger(__name__)
    
    logger.info("Ready to accept MCP connections via STDIO transport")

    try:
        # Run the server with STDIO transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("STDIO transport established, starting server run loop")

            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="solveit_mcp_server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully")
    except Exception as e:
        # Import here to avoid module-level import
        import traceback
        
        # Check if this is an ExceptionGroup (TaskGroup error)
        if hasattr(e, 'exceptions') and hasattr(e, '__class__') and 'ExceptionGroup' in str(type(e)):
            logger.critical(f"Server run loop failed with ExceptionGroup containing {len(e.exceptions)} exception(s):")
            for i, exc in enumerate(e.exceptions):
                logger.critical(f"  Exception {i+1}: {type(exc).__name__}: {exc}")
                logger.critical(f"  Traceback: {''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))}")
        else:
            # Handle regular exceptions
            logger.critical(f"Server run loop failed: {type(e).__name__}: {e}")
            logger.critical(f"Full traceback: {''.join(traceback.format_exception(type(e), e, e.__traceback__))}")
        
        logger.critical("Server terminating due to critical error")
        raise
    finally:
        logger.info("SOLVE-IT MCP Server shutdown completed")


def create_server() -> Server:
    """Create and configure the MCP server instance for testing."""
    return Server("solveit_mcp_server")


async def main() -> None:
    """Main entry point for the MCP server using official SDK."""
    # Configure logging first (before any other operations)
    configure_logging()
    logger = get_logger(__name__)

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="SOLVE-IT MCP Server")
    
    # Transport selection (currently only STDIO supported)
    parser.add_argument(
        "--transport", 
        choices=["stdio"], 
        default="stdio",
        help="Transport protocol (currently only stdio supported)"
    )
    
    args = parser.parse_args()

    # Log server startup
    logger.info("Starting SOLVE-IT MCP Server")
    logger.info("Server configuration: name=solveit_mcp_server, version=0.1.0")
    logger.info(f"Transport selected: {args.transport}")

    # Create the server
    try:
        server: Server = create_server()
        logger.info("MCP SDK server instance created successfully")
    except Exception as e:
        logger.critical(f"Failed to create MCP server instance: {e}")
        logger.critical("Server startup aborted - SDK initialization failed")
        raise

    # Initialize shared security configuration and middleware (Layer 1 protections)
    try:
        logger.info("Initializing shared security configuration")
        shared_security_manager = SharedSecurityConfig()
        shared_security_config = shared_security_manager.get_security_config()
        
        # Log shared security config stats
        sec_stats = shared_security_manager.get_security_config_stats()
        logger.info(
            f"Shared security configuration initialized: "
            f"max_input_size={sec_stats['max_input_size']}, "
            f"default_timeout={sec_stats['default_timeout']}s, "
            f"singleton_id: {sec_stats['singleton_id']}"
        )
        
        security = SecurityMiddleware(shared_security_config)
        logger.info("Security middleware initialized with Layer 1 protections")
    except Exception as e:
        logger.critical(f"Failed to initialize security middleware: {e}")
        logger.critical("Server startup aborted - security initialization failed")
        raise

    # PHASE 1: Initialize shared knowledge base ONCE
    try:
        logger.info("Initializing shared SOLVE-IT knowledge base (replaces 20x individual initialization)")
        shared_kb_manager = SharedKnowledgeBase()
        shared_kb = shared_kb_manager.get_knowledge_base()
        data_path = shared_kb_manager.get_data_path()
        
        # Log shared KB stats
        stats = shared_kb_manager.get_knowledge_base_stats()
        logger.info(
            f"Shared knowledge base initialized: {stats['techniques']} techniques, "
            f"{stats['weaknesses']} weaknesses, {stats['mitigations']} mitigations, "
            f"singleton_id: {stats['singleton_id']}"
        )
        
    except Exception as e:
        logger.critical(f"Failed to initialize shared knowledge base: {e}")
        logger.critical("Server startup aborted - shared knowledge base initialization failed")
        raise

    # PHASE 2: Initialize and register SOLVE-IT tools WITHOUT individual KB initialization
    try:
        logger.info("Creating SOLVE-IT tools with shared knowledge base architecture")
        
        # Create tools with init_kb=False to prevent individual KB initialization
        tools: list[BaseTool[Any]] = [
            # Core query tools
            GetDatabaseDescriptionTool(init_kb=False),
            SearchTool(init_kb=False),
            GetTechniqueDetailsTool(init_kb=False),
            GetWeaknessDetailsTool(init_kb=False),
            GetMitigationDetailsTool(init_kb=False),
            
            # Forward relationship query tools
            GetWeaknessesForTechniqueTool(init_kb=False),
            GetMitigationsForWeaknessTool(init_kb=False),
            
            # Reverse relationship query tools
            GetTechniquesForWeaknessTool(init_kb=False),
            GetWeaknessesForMitigationTool(init_kb=False),
            GetTechniquesForMitigationTool(init_kb=False),
            
            # Objective/Mapping management tools
            ListObjectivesTool(init_kb=False),
            GetTechniquesForObjectiveTool(init_kb=False),
            ListAvailableMappingsTool(init_kb=False),
            LoadObjectiveMappingTool(init_kb=False),
            
            # Bulk retrieval tools (concise format)
            GetAllTechniquesWithNameAndIdTool(init_kb=False),
            GetAllWeaknessesWithNameAndIdTool(init_kb=False),
            GetAllMitigationsWithNameAndIdTool(init_kb=False),
            
            # Bulk retrieval tools (full detail format)
            GetAllTechniquesWithFullDetailTool(init_kb=False),
            GetAllWeaknessesWithFullDetailTool(init_kb=False),
            GetAllMitigationsWithFullDetailTool(init_kb=False),
        ]

        # PHASE 3: Pass shared knowledge base to all tools
        logger.info("Configuring tools with shared knowledge base instance")
        for tool in tools:
            tool.set_shared_knowledge_base(shared_kb, data_path)

        # Auto-generate tool registry and metadata
        tool_registry: Dict[str, BaseTool[Any]] = {tool.name: tool for tool in tools}
        available_tools: list[str] = [tool.name for tool in tools]

        logger.info(f"Successfully configured {len(tools)} SOLVE-IT tools with shared architecture: {available_tools}")
        logger.info("All tools passed Layer 2 security configuration validation")
        logger.info(f"Performance improvement: 1x knowledge base initialization instead of {len(tools)}x")

    except Exception as e:
        logger.critical(f"Failed to initialize SOLVE-IT tools: {e}")
        logger.critical("Server startup aborted - tool initialization failed")
        raise

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools with comprehensive logging."""
        correlation_id = f"list_{uuid.uuid4().hex[:8]}"
        logger.info(
            "Tool list request received", extra={"correlation_id": correlation_id}
        )

        try:
            tool_list = []

            # Dynamically build tool list from registry
            for tool in tool_registry.values():
                tool_schema = tool.get_schema()
                tool_list.append(
                    types.Tool(
                        name=tool.name,
                        description=tool.description,
                        inputSchema=tool_schema,
                    )
                )

            logger.info(
                f"Tool list request completed: {len(tool_list)} tools available",
                extra={"correlation_id": correlation_id, "tools": available_tools},
            )

            return tool_list

        except Exception as e:
            logger.error(
                f"Tool list request failed: {e}",
                extra={"correlation_id": correlation_id},
            )
            raise

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent]:
        """Handle tool calls with comprehensive logging and performance tracking."""
        correlation_id = f"tool_{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Log request details (sanitized)
        arg_count = len(arguments) if arguments else 0
        logger.info(
            f"Tool call request: {name}",
            extra={
                "correlation_id": correlation_id,
                "tool_name": name,
                "arg_count": arg_count,
            },
        )

        try:
            if arguments is None:
                arguments = {}

            # LAYER 1 SECURITY: Request validation (automatic, cannot be bypassed)
            await security.validate_request(name, arguments)

            # Dynamic tool lookup
            if name not in tool_registry:
                error_msg = f"Unknown tool: {name}"
                logger.error(
                    error_msg,
                    extra={
                        "correlation_id": correlation_id,
                        "tool_name": name,
                        "available_tools": available_tools,
                    },
                )
                raise ValueError(error_msg)

            tool = tool_registry[name]
            logger.debug(
                f"Routing to {tool.name} tool", extra={"correlation_id": correlation_id}
            )

            # LAYER 2 SECURITY + Validation: Tool-level security and parameter validation
            validation_start = time.time()
            params = tool.validate_params(arguments)
            validation_time = time.time() - validation_start

            logger.debug(
                f"Parameter validation completed in {validation_time:.3f}s",
                extra={
                    "correlation_id": correlation_id,
                    "validation_time_ms": validation_time * 1000,
                },
            )

            # LAYER 1 SECURITY: Execution timeout (automatic, cannot be bypassed)
            tool_timeout = getattr(tool, 'execution_timeout', shared_security_config.default_timeout)
            
            async with security.execution_timeout(tool_timeout, name):
                execution_start = time.time()
                result = await tool.invoke(params)
                execution_time = time.time() - execution_start

            # LAYER 1 SECURITY: Response validation (automatic, cannot be bypassed)
            safe_result = await security.validate_response(result, name)

            # Total request time
            total_time = time.time() - start_time

            logger.info(
                f"Tool call completed successfully: {name}",
                extra={
                    "correlation_id": correlation_id,
                    "tool_name": name,
                    "execution_time_ms": execution_time * 1000,
                    "total_time_ms": total_time * 1000,
                    "result_length": len(safe_result),
                    "timeout_limit_ms": tool_timeout * 1000,
                },
            )

            return [types.TextContent(type="text", text=safe_result)]

        except SecurityError as e:
            # Calculate time even for failures
            total_time = time.time() - start_time

            # Log security violations with high severity
            logger.error(
                f"Security violation in tool call: {name} - {e}",
                extra={
                    "correlation_id": correlation_id,
                    "tool_name": name,
                    "error_type": "SecurityError",
                    "total_time_ms": total_time * 1000,
                    "security_violation": True,
                },
            )

            # Convert SecurityError to ValueError for MCP protocol
            raise ValueError(f"Security policy violation: {str(e)}")

        except Exception as e:
            # Calculate time even for failures
            total_time = time.time() - start_time

            # Log detailed error information
            logger.error(
                f"Tool call failed: {name} - {e}",
                extra={
                    "correlation_id": correlation_id,
                    "tool_name": name,
                    "error_type": type(e).__name__,
                    "total_time_ms": total_time * 1000,
                },
            )

            # For debugging, log the full exception details
            logger.debug(
                f"Full exception details: {e!r}",
                extra={"correlation_id": correlation_id},
            )

            # Re-raise the exception (SDK will handle the MCP error response)
            raise

    # Server startup completed successfully
    logger.info("Server initialization completed successfully")
    
    # Run server with selected transport (currently only STDIO supported)
    # Future enhancement: Add transport selection logic here
    # if args.transport == "sse":
    #     await run_sse_server(server)
    # else:
    #     await run_stdio_server(server)
    await run_stdio_server(server)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer interrupted by user", file=sys.stderr)
    except Exception as e:
        print(f"Server failed to start: {e}", file=sys.stderr)
        exit(1)
