"""Base class for SOLVE-IT MCP tools."""

import os
from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar

from .base import BaseTool, ToolParams
from utils.data_path import get_solve_it_data_path, validate_solve_it_data_path


P = TypeVar("P", bound=ToolParams)


class SolveItBaseTool(BaseTool[P], ABC):
    """
    Base class for SOLVE-IT MCP tools.
    
    This class extends the template's BaseTool to provide SOLVE-IT-specific
    functionality while maintaining compatibility with the template's design.
    
    ARCHITECTURE CHANGE: Tools no longer create individual knowledge base instances.
    Instead, they receive a shared knowledge base instance from the server during
    initialization, dramatically improving performance and memory usage.
    
    Previously: 20 tools × 1 KB instance each = 20x initialization (20 seconds)
    Now: 1 shared KB instance for all tools = 1x initialization (~1 second)
    """
    
    # Default security configuration for read-only knowledge base access
    execution_timeout: float = 45.0  # Longer timeout for data operations
    auto_sanitize_strings: bool = True
    require_path_validation: bool = False  # Most tools don't need path validation
    allowed_paths: list[str] = []  # Will be set by tools that need path validation
    
    def __init__(self, custom_data_path: Optional[str] = None, init_kb: bool = True) -> None:
        """
        Initialize SOLVE-IT tool with optional knowledge base initialization.
        
        Args:
            custom_data_path: Optional custom path to SOLVE-IT data directory.
                             If None, will use automatic path resolution.
            init_kb: Whether to initialize individual knowledge base (deprecated).
                    Should be False for shared architecture, True for legacy mode.
        """
        super().__init__()
        
        # Initialize knowledge base and data path attributes
        self.knowledge_base = None
        self.data_path = None
        
        # Resolve data path for backward compatibility and logging
        if custom_data_path or init_kb:
            self._resolve_data_path(custom_data_path)
        
        # Legacy mode: Initialize individual knowledge base (deprecated)
        if init_kb:
            self.logger.warning(
                f"Tool {self.name} using legacy individual knowledge base initialization. "
                "This is deprecated and causes performance issues. Use shared architecture instead."
            )
            self._init_knowledge_base()
            self.logger.info(f"SOLVE-IT tool {self.name} initialized with data path: {self.data_path}")
        else:
            # Modern mode: Wait for shared knowledge base to be set by server
            self.logger.debug(f"SOLVE-IT tool {self.name} created, awaiting shared knowledge base")
    
    def _resolve_data_path(self, custom_path: Optional[str] = None) -> None:
        """
        Resolve the data path for this tool instance.
        
        Args:
            custom_path: Optional custom path to SOLVE-IT data directory
            
        Raises:
            ValueError: If data path cannot be resolved or is invalid
        """
        try:
            # Use custom path from constructor, environment variable, or auto-detection
            if custom_path:
                self.data_path = custom_path
            else:
                # Check for environment variable first
                env_path = os.environ.get("SOLVE_IT_DATA_PATH")
                if env_path:
                    self.data_path = env_path
                else:
                    # Use auto-detection
                    self.data_path = get_solve_it_data_path()
            
            # Validate the resolved path
            if not validate_solve_it_data_path(self.data_path):
                raise ValueError(f"Invalid SOLVE-IT data path: {self.data_path}")
            
            self.logger.debug(f"Data path resolved for {self.name}: {self.data_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to resolve data path for {self.name}: {e}")
            raise ValueError(f"SOLVE-IT data path resolution failed: {e}")
    
    def set_shared_knowledge_base(self, shared_kb, data_path: str) -> None:
        """
        Set the shared knowledge base instance for this tool.
        
        This method is called by the server to provide the shared knowledge base
        instance to the tool, eliminating the need for individual initialization.
        
        Args:
            shared_kb: The shared KnowledgeBase instance
            data_path: The resolved data path for logging and compatibility
        """
        self.knowledge_base = shared_kb
        self.data_path = data_path
        
        # Log successful shared KB assignment
        self.logger.info(
            f"SOLVE-IT tool {self.name} configured with shared knowledge base "
            f"(singleton_id: {id(shared_kb)})"
        )
        self.logger.debug(f"Tool {self.name} data path: {data_path}")
    
    def _init_knowledge_base(self) -> None:
        """
        Initialize individual SOLVE-IT knowledge base (LEGACY/DEPRECATED).
        
        This method is deprecated and causes the 20x initialization performance issue.
        It's kept for backward compatibility but should not be used in production.
        
        PERFORMANCE IMPACT: Each call loads 117 techniques, 188 weaknesses, 137 mitigations
        and builds reverse indices. With 20 tools, this results in 20x duplication.
        
        Use set_shared_knowledge_base() instead for modern architecture.
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.insert(0, str(Path(self.data_path).parent))
            
            from solve_it_library import KnowledgeBase
            
            # Initialize knowledge base with solve-it.json as default mapping
            self.knowledge_base = KnowledgeBase(
                base_path=str(Path(self.data_path).parent),
                mapping_file="solve-it.json"
            )
            
            self.logger.debug(f"Individual knowledge base initialized for {self.name} (DEPRECATED)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base for {self.name}: {e}")
            raise ValueError(f"SOLVE-IT knowledge base initialization failed: {e}")
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded knowledge base.
        
        Returns:
            Dict[str, Any]: Statistics about techniques, weaknesses, mitigations
        """
        try:
            if self.knowledge_base is None:
                return {"error": "Knowledge base not initialized"}
            
            return {
                "techniques": len(self.knowledge_base.list_techniques()),
                "weaknesses": len(self.knowledge_base.list_weaknesses()),
                "mitigations": len(self.knowledge_base.list_mitigations()),
                "objectives": len(self.knowledge_base.list_objectives()),
                "current_mapping": self.knowledge_base.current_mapping_name,
                "data_path": self.data_path,
                "singleton_id": id(self.knowledge_base),  # For debugging shared instance
                "tool_name": self.name
            }
        except Exception as e:
            self.logger.error(f"Failed to get knowledge base stats: {e}")
            return {"error": str(e)}
    
    def handle_knowledge_base_error(self, error: Exception, operation: str) -> str:
        """
        Handle knowledge base errors with consistent logging and user-friendly messages.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
            
        Returns:
            str: User-friendly error message
        """
        # Check if knowledge base is properly initialized
        if self.knowledge_base is None:
            error_msg = f"Knowledge base not initialized for tool {self.name} during {operation}"
            self.logger.error(error_msg)
            return "Tool not properly initialized. Please contact support."
        
        error_msg = f"Error in {operation}: {str(error)}"
        self.logger.error(error_msg, extra={
            "tool_name": self.name,
            "singleton_id": id(self.knowledge_base),
            "operation": operation
        })
        
        # Return user-friendly error message
        if "not found" in str(error).lower():
            return f"Item not found during {operation}. Please check the ID and try again."
        elif "invalid" in str(error).lower():
            return f"Invalid input for {operation}. Please check your parameters."
        else:
            return f"An error occurred during {operation}. Please try again or contact support."
