"""Shared Knowledge Base Manager for SOLVE-IT MCP Server.

This module provides a singleton pattern for managing the SOLVE-IT knowledge base
across all tools, eliminating the performance issue where each tool was creating
its own knowledge base instance.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .logging import get_logger
from .data_path import get_solve_it_data_path, validate_solve_it_data_path


class SharedKnowledgeBase:
    """
    Singleton manager for SOLVE-IT knowledge base.
    
    This class ensures that only one KnowledgeBase instance is created and shared
    across all tools, dramatically improving startup performance and memory usage.
    
    Previously: 20 tools × 1 KB instance each = 20x initialization (20 seconds)
    Now: 1 KB instance shared by 20 tools = 1x initialization (~1 second)
    """
    
    _instance: Optional['SharedKnowledgeBase'] = None
    _knowledge_base = None
    _data_path: Optional[str] = None
    _logger = None
    
    def __new__(cls, data_path: Optional[str] = None):
        """
        Create or return the singleton instance.
        
        Args:
            data_path: Optional path to SOLVE-IT data directory.
                      If None, will use environment variable or auto-detection.
        
        Returns:
            SharedKnowledgeBase: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logger = get_logger(__name__)
            cls._logger.info("Creating shared knowledge base singleton instance")
            cls._instance._init_knowledge_base(data_path)
        return cls._instance
    
    def _init_knowledge_base(self, custom_data_path: Optional[str] = None) -> None:
        """
        Initialize the knowledge base once for all tools.
        
        This method performs the expensive initialization operations that were
        previously done 20 times (once per tool). Now it's done once and shared.
        
        Args:
            custom_data_path: Optional custom path to SOLVE-IT data directory
            
        Raises:
            ValueError: If data path cannot be resolved or knowledge base fails to load
        """
        try:
            # Resolve data path
            self._resolve_data_path(custom_data_path)
            
            # Initialize knowledge base
            self._create_knowledge_base()
            
            # Log successful initialization
            stats = self.get_knowledge_base_stats()
            self._logger.info(
                f"Shared knowledge base initialized successfully: "
                f"{stats['techniques']} techniques, {stats['weaknesses']} weaknesses, "
                f"{stats['mitigations']} mitigations"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to initialize shared knowledge base: {e}")
            raise ValueError(f"Shared knowledge base initialization failed: {e}")
    
    def _resolve_data_path(self, custom_path: Optional[str] = None) -> None:
        """
        Resolve the data path for the shared knowledge base.
        
        Priority order:
        1. custom_path parameter (for testing/override)
        2. SOLVE_IT_DATA_PATH environment variable 
        3. Auto-detection using get_solve_it_data_path()
        
        Args:
            custom_path: Optional custom path to SOLVE-IT data directory
            
        Raises:
            ValueError: If data path cannot be resolved or is invalid
        """
        try:
            if custom_path:
                self._data_path = custom_path
                self._logger.debug(f"Using custom data path: {custom_path}")
            else:
                # Check for environment variable first
                env_path = os.environ.get("SOLVE_IT_DATA_PATH")
                if env_path:
                    self._data_path = env_path
                    self._logger.debug(f"Using environment data path: {env_path}")
                else:
                    # Use auto-detection
                    self._data_path = get_solve_it_data_path()
                    self._logger.debug(f"Using auto-detected data path: {self._data_path}")
            
            # Validate the resolved path
            if not validate_solve_it_data_path(self._data_path):
                raise ValueError(f"Invalid SOLVE-IT data path: {self._data_path}")
            
            self._logger.info(f"Data path resolved: {self._data_path}")
            
        except Exception as e:
            self._logger.error(f"Failed to resolve data path: {e}")
            raise ValueError(f"SOLVE-IT data path resolution failed: {e}")
    
    def _create_knowledge_base(self) -> None:
        """
        Create the SOLVE-IT knowledge base instance.
        
        This method sets up the KnowledgeBase instance that will be shared
        by all tools. It includes the solve-it library path setup and
        knowledge base initialization.
        
        Raises:
            ValueError: If knowledge base creation fails
        """
        try:
            # Import here to avoid circular imports and ensure path is set
            parent_path = str(Path(self._data_path).parent)
            
            # Ensure the parent path (which contains solve_it_library) is in sys.path
            if parent_path not in sys.path:
                sys.path.insert(0, parent_path)
                self._logger.debug(f"Added to sys.path: {parent_path}")
            
            # Debug: Check if solve_it_library directory exists
            solve_it_lib_path = Path(parent_path) / "solve_it_library"
            if not solve_it_lib_path.exists():
                self._logger.error(f"solve_it_library directory not found at: {solve_it_lib_path}")
                raise ImportError(f"solve_it_library directory not found at: {solve_it_lib_path}")
            
            self._logger.debug(f"Found solve_it_library at: {solve_it_lib_path}")
            
            # Import the KnowledgeBase class
            from solve_it_library import KnowledgeBase
            
            # Initialize knowledge base with solve-it.json as default mapping
            self._knowledge_base = KnowledgeBase(
                base_path=parent_path,
                mapping_file="solve-it.json"
            )
            
            self._logger.debug("Knowledge base instance created successfully")
            
        except ImportError as e:
            self._logger.error(f"Failed to import solve_it_library: {e}")
            self._logger.error(f"Current sys.path: {sys.path[:3]}...")  # Show first few entries
            self._logger.error(f"Expected solve_it_library at: {parent_path}/solve_it_library")
            raise ValueError(f"SOLVE-IT knowledge base import failed: {e}")
        except Exception as e:
            self._logger.error(f"Failed to create knowledge base: {e}")
            raise ValueError(f"SOLVE-IT knowledge base creation failed: {e}")
    
    def get_knowledge_base(self):
        """
        Get the shared knowledge base instance.
        
        Returns:
            KnowledgeBase: The shared SOLVE-IT knowledge base instance
            
        Raises:
            RuntimeError: If knowledge base hasn't been initialized
        """
        if self._knowledge_base is None:
            raise RuntimeError("Shared knowledge base not initialized")
        return self._knowledge_base
    
    def get_data_path(self) -> str:
        """
        Get the resolved data path.
        
        Returns:
            str: Path to SOLVE-IT data directory
            
        Raises:
            RuntimeError: If data path hasn't been resolved
        """
        if self._data_path is None:
            raise RuntimeError("Data path not resolved")
        return self._data_path
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded knowledge base.
        
        Returns:
            Dict[str, Any]: Statistics about techniques, weaknesses, mitigations, etc.
        """
        try:
            if self._knowledge_base is None:
                return {"error": "Knowledge base not initialized"}
            
            return {
                "techniques": len(self._knowledge_base.list_techniques()),
                "weaknesses": len(self._knowledge_base.list_weaknesses()),
                "mitigations": len(self._knowledge_base.list_mitigations()),
                "objectives": len(self._knowledge_base.list_objectives()),
                "current_mapping": self._knowledge_base.current_mapping_name,
                "data_path": self._data_path,
                "singleton_id": id(self._knowledge_base)  # For debugging shared instance
            }
        except Exception as e:
            self._logger.error(f"Failed to get knowledge base stats: {e}")
            return {"error": str(e)}
    
    @classmethod
    def reset_singleton(cls) -> None:
        """
        Reset the singleton instance.
        
        This method is primarily for testing purposes, allowing tests to
        create fresh instances with different configurations.
        
        Warning: This should not be used in production code.
        """
        cls._instance = None
        cls._knowledge_base = None
        cls._data_path = None
        if cls._logger:
            cls._logger.debug("Singleton instance reset")


def get_shared_knowledge_base(data_path: Optional[str] = None):
    """
    Convenience function to get the shared knowledge base instance.
    
    Args:
        data_path: Optional path to SOLVE-IT data directory
        
    Returns:
        KnowledgeBase: The shared SOLVE-IT knowledge base instance
    """
    manager = SharedKnowledgeBase(data_path)
    return manager.get_knowledge_base()


def get_shared_knowledge_base_stats(data_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get knowledge base statistics.
    
    Args:
        data_path: Optional path to SOLVE-IT data directory
        
    Returns:
        Dict[str, Any]: Knowledge base statistics
    """
    manager = SharedKnowledgeBase(data_path)
    return manager.get_knowledge_base_stats()
