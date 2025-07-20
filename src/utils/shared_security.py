"""Shared Security Configuration Manager for SOLVE-IT MCP Server.

This module provides a singleton pattern for managing the security configuration
across all tools, eliminating the performance issue where each tool was creating
its own security configuration instance.
"""

from typing import Optional
import logging

from .logging import get_logger
from .security_middleware import SecurityConfig


class SharedSecurityConfig:
    """
    Singleton manager for security configuration.
    
    This class ensures that only one SecurityConfig instance is created and shared
    across all tools, eliminating the 20x "Security configuration initialized" logs.
    
    Previously: 20 tools × 1 SecurityConfig instance each = 20x initialization
    Now: 1 SecurityConfig instance shared by 20 tools = 1x initialization
    """
    
    _instance: Optional['SharedSecurityConfig'] = None
    _security_config: Optional[SecurityConfig] = None
    _logger = None
    
    def __new__(cls):
        """
        Create or return the singleton instance.
        
        Returns:
            SharedSecurityConfig: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logger = get_logger(__name__)
            cls._logger.info("Creating shared security configuration singleton instance")
            cls._instance._init_security_config()
        return cls._instance
    
    def _init_security_config(self) -> None:
        """
        Initialize the security configuration once for all tools.
        """
        try:
            # Initialize security configuration
            self._security_config = SecurityConfig()
            
            # Log successful initialization
            self._logger.info(
                f"Shared security configuration initialized successfully: "
                f"max_input_size={self._security_config.max_input_size}, "
                f"max_output_size={self._security_config.max_output_size}, "
                f"default_timeout={self._security_config.default_timeout}"
            )
            
        except Exception as e:
            self._logger.error(f"Failed to initialize shared security configuration: {e}")
            raise ValueError(f"Shared security configuration initialization failed: {e}")
    
    def get_security_config(self) -> SecurityConfig:
        """
        Get the shared security configuration instance.
        
        Returns:
            SecurityConfig: The shared security configuration instance
            
        Raises:
            RuntimeError: If security configuration hasn't been initialized
        """
        if self._security_config is None:
            raise RuntimeError("Shared security configuration not initialized")
        return self._security_config
    
    def get_security_config_stats(self) -> dict:
        """
        Get statistics about the loaded security configuration.
        
        Returns:
            dict: Statistics about security configuration
        """
        try:
            if self._security_config is None:
                return {"error": "Security configuration not initialized"}
            
            return {
                "max_input_size": self._security_config.max_input_size,
                "max_output_size": self._security_config.max_output_size,
                "default_timeout": self._security_config.default_timeout,
                "max_timeout": self._security_config.max_timeout,
                "rate_limit_per_minute": self._security_config.rate_limit_per_minute,
                "output_rate_limit": self._security_config.output_rate_limit,
                "singleton_id": id(self._security_config)  # For debugging shared instance
            }
        except Exception as e:
            self._logger.error(f"Failed to get security configuration stats: {e}")
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
        cls._security_config = None
        if cls._logger:
            cls._logger.debug("Security singleton instance reset")


def get_shared_security_config() -> SecurityConfig:
    """
    Convenience function to get the shared security configuration instance.
    
    Returns:
        SecurityConfig: The shared security configuration instance
    """
    manager = SharedSecurityConfig()
    return manager.get_security_config()


def get_shared_security_config_stats() -> dict:
    """
    Convenience function to get security configuration statistics.
    
    Returns:
        dict: Security configuration statistics
    """
    manager = SharedSecurityConfig()
    return manager.get_security_config_stats()
