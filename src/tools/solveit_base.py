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
    Each tool manages its own data path resolution, making tools self-contained
    and following the template's tool-centric philosophy.
    """
    
    # Default security configuration for read-only knowledge base access
    execution_timeout: float = 45.0  # Longer timeout for data operations
    auto_sanitize_strings: bool = True
    require_path_validation: bool = False  # SOLVE-IT data is read-only
    
    def __init__(self, custom_data_path: Optional[str] = None) -> None:
        """
        Initialize SOLVE-IT tool with data path resolution.
        
        Args:
            custom_data_path: Optional custom path to SOLVE-IT data directory.
                             If None, will use automatic path resolution.
        """
        super().__init__()
        
        # Resolve data path for this tool instance
        self._resolve_data_path(custom_data_path)
        
        # Initialize SOLVE-IT knowledge base
        self._init_knowledge_base()
        
        self.logger.info(f"SOLVE-IT tool {self.name} initialized with data path: {self.data_path}")
    
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
    
    def _init_knowledge_base(self) -> None:
        """
        Initialize the SOLVE-IT knowledge base.
        
        This method sets up the KnowledgeBase instance that will be used
        by the tool. Each tool gets its own instance to ensure isolation.
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
            
            self.logger.debug(f"Knowledge base initialized for {self.name}")
            
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
            return {
                "techniques": len(self.knowledge_base.list_techniques()),
                "weaknesses": len(self.knowledge_base.list_weaknesses()),
                "mitigations": len(self.knowledge_base.list_mitigations()),
                "objectives": len(self.knowledge_base.list_objectives()),
                "current_mapping": self.knowledge_base.current_mapping_name,
                "data_path": self.data_path
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
        error_msg = f"Error in {operation}: {str(error)}"
        self.logger.error(error_msg, extra={"tool_name": self.name})
        
        # Return user-friendly error message
        if "not found" in str(error).lower():
            return f"Item not found during {operation}. Please check the ID and try again."
        elif "invalid" in str(error).lower():
            return f"Invalid input for {operation}. Please check your parameters."
        else:
            return f"An error occurred during {operation}. Please try again or contact support."
