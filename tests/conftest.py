"""Test configuration and fixtures for SOLVE-IT MCP server tests."""

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
from typing import Any, Dict, List, Optional

import pytest


@pytest.fixture
def mock_knowledge_base():
    """Mock SOLVE-IT KnowledgeBase with sample data."""
    mock_kb = MagicMock()
    
    # Sample test data
    sample_technique = {
        "id": "T1001",
        "name": "Test Technique",
        "description": "A test technique for unit testing",
        "weaknesses": ["W1001", "W1002"]
    }
    
    sample_weakness = {
        "id": "W1001",
        "name": "Test Weakness",
        "description": "A test weakness for unit testing",
        "mitigations": ["M1001"]
    }
    
    sample_mitigation = {
        "id": "M1001",
        "name": "Test Mitigation",
        "description": "A test mitigation for unit testing"
    }
    
    # Mock all the methods
    mock_kb.get_technique.return_value = sample_technique
    mock_kb.get_weakness.return_value = sample_weakness
    mock_kb.get_mitigation.return_value = sample_mitigation
    
    # Mock search results
    mock_kb.search.return_value = {
        "techniques": [sample_technique],
        "weaknesses": [sample_weakness],
        "mitigations": [sample_mitigation]
    }
    
    # Mock relationship methods
    mock_kb.get_weaknesses_for_technique.return_value = [sample_weakness]
    mock_kb.get_mitigations_for_weakness.return_value = [sample_mitigation]
    mock_kb.get_techniques_for_weakness.return_value = [sample_technique]
    mock_kb.get_weaknesses_for_mitigation.return_value = [sample_weakness]
    mock_kb.get_techniques_for_mitigation.return_value = [sample_technique]
    
    # Mock objective methods
    mock_kb.list_objectives.return_value = ["Test Objective 1", "Test Objective 2"]
    mock_kb.get_techniques_for_objective.return_value = [sample_technique]
    mock_kb.list_available_mappings.return_value = ["solve-it.json", "carrier.json"]
    mock_kb.load_objective_mapping.return_value = True
    mock_kb.current_mapping_name = "solve-it.json"
    
    # Mock list methods
    mock_kb.list_techniques.return_value = ["T1001", "T1002"]
    mock_kb.list_weaknesses.return_value = ["W1001", "W1002"]
    mock_kb.list_mitigations.return_value = ["M1001", "M1002"]
    
    # Mock bulk retrieval methods
    mock_kb.get_all_techniques_with_name_and_id.return_value = [
        {"id": "T1001", "name": "Test Technique 1"},
        {"id": "T1002", "name": "Test Technique 2"}
    ]
    mock_kb.get_all_weaknesses_with_name_and_id.return_value = [
        {"id": "W1001", "name": "Test Weakness 1"},
        {"id": "W1002", "name": "Test Weakness 2"}
    ]
    mock_kb.get_all_mitigations_with_name_and_id.return_value = [
        {"id": "M1001", "name": "Test Mitigation 1"},
        {"id": "M1002", "name": "Test Mitigation 2"}
    ]
    
    # Mock full detail methods
    mock_kb.get_all_techniques_with_full_detail.return_value = [sample_technique]
    mock_kb.get_all_weaknesses_with_full_detail.return_value = [sample_weakness]
    mock_kb.get_all_mitigations_with_full_detail.return_value = [sample_mitigation]
    
    return mock_kb


@pytest.fixture
def mock_data_path(tmp_path):
    """Mock data path with temporary directory."""
    # Create a temporary SOLVE-IT data structure
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Create sample data files
    (data_dir / "solve-it.json").write_text(json.dumps({
        "Test Objective 1": ["T1001"],
        "Test Objective 2": ["T1002"]
    }))
    
    (data_dir / "carrier.json").write_text(json.dumps({
        "Carrier Objective": ["T1001", "T1002"]
    }))
    
    return str(data_dir)


@pytest.fixture
def mock_solve_it_environment(mock_data_path, mock_knowledge_base):
    """Mock the entire SOLVE-IT environment."""
    # Create a mock solve_it_library module
    mock_solve_it_library = MagicMock()
    mock_solve_it_library.KnowledgeBase = MagicMock(return_value=mock_knowledge_base)
    
    with patch('utils.data_path.get_solve_it_data_path') as mock_get_path, \
         patch('utils.data_path.validate_solve_it_data_path') as mock_validate, \
         patch.dict('sys.modules', {'solve_it_library': mock_solve_it_library}):
        
        # Mock data path functions
        mock_get_path.return_value = mock_data_path
        mock_validate.return_value = True
        
        yield {
            'data_path': mock_data_path,
            'knowledge_base': mock_knowledge_base,
            'kb_class': mock_solve_it_library.KnowledgeBase
        }


@pytest.fixture
def sample_tool_responses():
    """Sample responses for various tool operations."""
    return {
        'database_description': {
            "database_name": "SOLVE-IT Digital Forensics Knowledge Base",
            "description": "A systematic digital forensics knowledge base",
            "statistics": {
                "techniques": 2,
                "weaknesses": 2,
                "mitigations": 2,
                "objectives": 2,
                "current_mapping": "solve-it.json",
                "data_path": "/test/path"
            }
        },
        'search_results': {
            "techniques": [{"id": "T1001", "name": "Test Technique"}],
            "weaknesses": [{"id": "W1001", "name": "Test Weakness"}],
            "mitigations": [{"id": "M1001", "name": "Test Mitigation"}]
        },
        'technique_details': {
            "id": "T1001",
            "name": "Test Technique",
            "description": "A test technique"
        },
        'weakness_details': {
            "id": "W1001",
            "name": "Test Weakness",
            "description": "A test weakness"
        },
        'mitigation_details': {
            "id": "M1001",
            "name": "Test Mitigation",
            "description": "A test mitigation"
        }
    }


@pytest.fixture
def invalid_parameters():
    """Sample invalid parameters for testing validation."""
    return {
        'empty_string': "",
        'whitespace_only': "   ",
        'none_value': None,
        'invalid_id_format': "INVALID123",
        'missing_prefix': "1001",
        'wrong_prefix': "X1001"
    }


@pytest.fixture
def error_scenarios():
    """Sample error scenarios for testing error handling."""
    return {
        'not_found_error': Exception("Item not found"),
        'invalid_parameter_error': Exception("Invalid parameter"),
        'file_not_found_error': FileNotFoundError("Data file not found"),
        'permission_error': PermissionError("Access denied"),
        'generic_error': Exception("Unexpected error occurred")
    }


@pytest.fixture
def mcp_server_config():
    """Configuration for MCP server testing."""
    return {
        'server_name': 'solveit_mcp_server',
        'version': '1.0.0',
        'transport': 'stdio',
        'expected_tool_count': 20
    }


# Test utilities
def validate_json_response(response: str) -> Dict[str, Any]:
    """Validate that a response is valid JSON and return parsed data."""
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        pytest.fail(f"Response is not valid JSON: {e}\nResponse: {response}")


def assert_error_response(response: str, expected_error_type: str = None):
    """Assert that a response contains an error message."""
    assert isinstance(response, str)
    assert "error" in response.lower() or "not found" in response.lower()
    
    if expected_error_type:
        assert expected_error_type.lower() in response.lower()
