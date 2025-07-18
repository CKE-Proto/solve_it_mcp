"""Unit tests for data path resolution utilities."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from solveit_mcp_server.utils.data_path import (
    get_solve_it_data_path,
    validate_solve_it_data_path
)


class TestGetSolveItDataPath:
    """Test the get_solve_it_data_path function."""
    
    def test_environment_variable_path(self):
        """Test that environment variable takes precedence."""
        test_path = "/custom/solve-it/path"
        with patch.dict(os.environ, {'SOLVE_IT_DATA_PATH': test_path}):
            with patch('solveit_mcp_server.utils.data_path.validate_solve_it_data_path', return_value=True):
                result = get_solve_it_data_path()
                assert result == test_path
    
    def test_custom_path_provided(self, tmp_path):
        """Test that custom path takes precedence."""
        # Create a valid data directory
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        result = get_solve_it_data_path(str(data_dir))
        assert result == str(data_dir)
    
    def test_custom_path_with_parent_directory(self, tmp_path):
        """Test custom path pointing to parent directory."""
        # Create a solve-it directory with data subdirectory
        solve_it_dir = tmp_path / "solve-it-main"
        solve_it_dir.mkdir()
        data_dir = solve_it_dir / "data"
        data_dir.mkdir()
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        result = get_solve_it_data_path(str(solve_it_dir))
        assert result == str(data_dir)
    
    def test_invalid_custom_path_raises_error(self):
        """Test that invalid custom path raises error."""
        with pytest.raises(FileNotFoundError, match="Custom path .* does not exist"):
            get_solve_it_data_path("/invalid/path")
    
    def test_environment_variable_with_data_subdir(self, tmp_path):
        """Test environment variable pointing to parent with data subdir."""
        # Create a solve-it directory with data subdirectory
        solve_it_dir = tmp_path / "solve-it-main"
        solve_it_dir.mkdir()
        data_dir = solve_it_dir / "data"
        data_dir.mkdir()
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        with patch.dict(os.environ, {'SOLVE_IT_DATA_PATH': str(solve_it_dir)}):
            result = get_solve_it_data_path()
            assert result == str(data_dir)
    
    def test_no_path_found_raises_error(self):
        """Test that error is raised when no path is found."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('pathlib.Path.exists', return_value=False):
                with pytest.raises(FileNotFoundError, match="SOLVE-IT data directory not found"):
                    get_solve_it_data_path()


class TestValidateSolveItDataPath:
    """Test the validate_solve_it_data_path function."""
    
    def test_valid_path_with_required_files(self, tmp_path):
        """Test validation with all required files present."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create required files
        (data_dir / "solve-it.json").write_text('{"test": "data"}')
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        assert validate_solve_it_data_path(str(data_dir)) is True
    
    def test_nonexistent_path(self):
        """Test validation with nonexistent path."""
        assert validate_solve_it_data_path("/nonexistent/path") is False
    
    def test_missing_solve_it_json(self, tmp_path):
        """Test validation with missing solve-it.json file."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create directories but not solve-it.json
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        assert validate_solve_it_data_path(str(data_dir)) is False
    
    def test_missing_techniques_directory(self, tmp_path):
        """Test validation with missing techniques directory."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create solve-it.json but not techniques directory
        (data_dir / "solve-it.json").write_text('{"test": "data"}')
        (data_dir / "weaknesses").mkdir()
        (data_dir / "mitigations").mkdir()
        
        assert validate_solve_it_data_path(str(data_dir)) is False
    
    def test_missing_weaknesses_directory(self, tmp_path):
        """Test validation with missing weaknesses directory."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create solve-it.json but not weaknesses directory
        (data_dir / "solve-it.json").write_text('{"test": "data"}')
        (data_dir / "techniques").mkdir()
        (data_dir / "mitigations").mkdir()
        
        assert validate_solve_it_data_path(str(data_dir)) is False
    
    def test_missing_mitigations_directory(self, tmp_path):
        """Test validation with missing mitigations directory."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        
        # Create solve-it.json but not mitigations directory
        (data_dir / "solve-it.json").write_text('{"test": "data"}')
        (data_dir / "techniques").mkdir()
        (data_dir / "weaknesses").mkdir()
        
        assert validate_solve_it_data_path(str(data_dir)) is False
    
    def test_file_instead_of_directory(self, tmp_path):
        """Test validation when path points to a file instead of directory."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        assert validate_solve_it_data_path(str(test_file)) is False
