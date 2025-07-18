"""Data path configuration utilities for SOLVE-IT MCP Server."""

import os
from pathlib import Path
from typing import Optional

from .logging import get_logger

logger = get_logger(__name__)


def get_solve_it_data_path(custom_path: Optional[str] = None) -> str:
    """
    Get the path to the SOLVE-IT data directory.
    
    Args:
        custom_path: Optional custom path to SOLVE-IT data directory
        
    Returns:
        str: Path to SOLVE-IT data directory
        
    Raises:
        FileNotFoundError: If data directory cannot be found
        
    The function attempts to locate the SOLVE-IT data directory in this order:
    1. Custom path provided via parameter
    2. SOLVE_IT_DATA_PATH environment variable
    3. Adjacent solve-it-main directory (../solve-it-main)
    4. Current directory solve-it-main subdirectory (./solve-it-main)
    """
    
    # Try custom path first
    if custom_path:
        data_path = Path(custom_path)
        if data_path.exists() and data_path.is_dir():
            # Check if it's the root directory or the data subdirectory
            if (data_path / "data").exists():
                return str(data_path / "data")
            elif (data_path / "techniques").exists():
                return str(data_path)
            else:
                raise FileNotFoundError(f"Custom path {custom_path} does not contain SOLVE-IT data")
        else:
            raise FileNotFoundError(f"Custom path {custom_path} does not exist")
    
    # Try environment variable
    env_path = os.environ.get("SOLVE_IT_DATA_PATH")
    if env_path:
        data_path = Path(env_path)
        if data_path.exists() and data_path.is_dir():
            # Check if it's the root directory or the data subdirectory
            if (data_path / "data").exists():
                return str(data_path / "data")
            elif (data_path / "techniques").exists():
                return str(data_path)
            else:
                raise FileNotFoundError(f"Environment path {env_path} does not contain SOLVE-IT data")
        else:
            raise FileNotFoundError(f"Environment path {env_path} does not exist")
    
    # Try adjacent solve-it-main directory (default expected location)
    current_dir = Path(__file__).parent.parent.parent.parent  # Go up from utils to project root
    adjacent_path = current_dir / "../solve-it-main"
    
    if adjacent_path.exists():
        resolved_path = adjacent_path.resolve()
        data_path = resolved_path / "data"
        if data_path.exists() and data_path.is_dir():
            logger.info(f"Found SOLVE-IT data at default location: {data_path}")
            return str(data_path)
    
    # Try current directory solve-it-main subdirectory
    current_solve_it = current_dir / "solve-it-main"
    if current_solve_it.exists():
        data_path = current_solve_it / "data"
        if data_path.exists() and data_path.is_dir():
            logger.info(f"Found SOLVE-IT data in current directory: {data_path}")
            return str(data_path)
    
    # If nothing found, provide helpful error message
    raise FileNotFoundError(
        "SOLVE-IT data directory not found. Please ensure one of the following:\n"
        "1. Place solve-it-main directory adjacent to this server directory\n"
        "2. Set SOLVE_IT_DATA_PATH environment variable\n"
        "3. Use --data-path argument\n"
        f"Searched locations:\n"
        f"  - Custom path: {custom_path}\n"
        f"  - Environment: {env_path}\n"
        f"  - Adjacent: {adjacent_path.resolve()}\n"
        f"  - Current: {current_solve_it.resolve()}"
    )


def validate_solve_it_data_path(data_path: str) -> bool:
    """
    Validate that the provided path contains SOLVE-IT data.
    
    Args:
        data_path: Path to validate
        
    Returns:
        bool: True if path contains valid SOLVE-IT data structure
    """
    path = Path(data_path)
    
    if not path.exists() or not path.is_dir():
        return False
    
    # Check for required subdirectories
    required_dirs = ["techniques", "weaknesses", "mitigations"]
    for dir_name in required_dirs:
        if not (path / dir_name).exists():
            return False
    
    # Check for objective mapping files
    mapping_files = ["solve-it.json", "carrier.json", "dfrws.json"]
    parent_dir = path.parent
    has_mapping = any((parent_dir / mapping_file).exists() for mapping_file in mapping_files)
    
    if not has_mapping:
        logger.warning(f"No objective mapping files found in {parent_dir}")
    
    return True
