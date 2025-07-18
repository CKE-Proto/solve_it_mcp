"""Unit tests for SolveItBaseTool base class."""

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

import pytest

from solveit_mcp_server.tools.solveit_base import SolveItBaseTool, ToolParams
from conftest import validate_json_response


class MockToolParams(ToolParams):
    """Mock parameters class for testing SolveItBaseTool."""
    test_param: str = "test_value"


class MockSolveItBaseTool(SolveItBaseTool[MockToolParams]):
    """Mock implementation of SolveItBaseTool."""
    
    name = "test_tool"
    description = "A test tool for unit testing"
    Params = MockToolParams
    
    async def invoke(self, params: MockToolParams) -> str:
        """Test invoke method."""
        return json.dumps({"test": params.test_param})


class TestSolveItBaseToolInitialization:
    """Test SolveItBaseTool initialization."""
    
    def test_init_with_custom_data_path(self, mock_solve_it_environment):
        """Test initialization with custom data path."""
        custom_path = "/custom/data/path"
        
        with patch.object(MockSolveItBaseTool, '_resolve_data_path') as mock_resolve, \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base') as mock_init_kb:
            
            # Set up side effects to properly set attributes
            def resolve_side_effect(instance, path):
                instance.data_path = path or custom_path
            
            def init_kb_side_effect(instance):
                instance.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            mock_resolve.side_effect = lambda path: setattr(mock_resolve, '_instance', mock_resolve.__self__) or setattr(mock_resolve.__self__, 'data_path', path or custom_path)
            mock_init_kb.side_effect = lambda: setattr(mock_init_kb.__self__, 'knowledge_base', mock_solve_it_environment['knowledge_base'])
            
            tool = MockSolveItBaseTool(custom_data_path=custom_path)
            
            mock_resolve.assert_called_once_with(custom_path)
            mock_init_kb.assert_called_once()
    
    def test_init_without_custom_data_path(self, mock_solve_it_environment):
        """Test initialization without custom data path."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path') as mock_resolve, \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base') as mock_init_kb:
            
            tool = MockSolveItBaseTool()
            
            mock_resolve.assert_called_once_with(None)
            mock_init_kb.assert_called_once()
    
    def test_security_configuration_defaults(self, mock_solve_it_environment):
        """Test that security configuration has appropriate defaults."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            
            assert tool.execution_timeout == 45.0
            assert tool.auto_sanitize_strings is True
            assert tool.require_path_validation is False


class TestDataPathResolution:
    """Test data path resolution functionality."""
    
    def test_resolve_data_path_with_custom_path(self, mock_solve_it_environment):
        """Test resolving data path with custom path."""
        custom_path = "/custom/data/path"
        
        with patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            with patch('solveit_mcp_server.utils.data_path.validate_solve_it_data_path', return_value=True):
                tool = MockSolveItBaseTool(custom_data_path=custom_path)
                
                assert tool.data_path == custom_path
    
    def test_resolve_data_path_with_environment_variable(self, mock_solve_it_environment):
        """Test resolving data path with environment variable."""
        env_path = "/env/data/path"
        
        with patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            with patch.dict(os.environ, {'SOLVE_IT_DATA_PATH': env_path}):
                with patch('solveit_mcp_server.utils.data_path.validate_solve_it_data_path', return_value=True):
                    tool = MockSolveItBaseTool()
                    
                    assert tool.data_path == env_path
    
    def test_resolve_data_path_with_auto_detection(self, mock_solve_it_environment):
        """Test resolving data path with auto-detection."""
        auto_path = "/auto/detected/path"
        
        with patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            with patch.dict(os.environ, {}, clear=True):
                with patch('solveit_mcp_server.utils.data_path.get_solve_it_data_path', return_value=auto_path):
                    with patch('solveit_mcp_server.utils.data_path.validate_solve_it_data_path', return_value=True):
                        tool = MockSolveItBaseTool()
                        
                        assert tool.data_path == auto_path
    
    def test_resolve_data_path_validation_failure(self, mock_solve_it_environment):
        """Test data path resolution with validation failure."""
        invalid_path = "/invalid/path"
        
        with patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            with patch('solveit_mcp_server.utils.data_path.validate_solve_it_data_path', return_value=False):
                with pytest.raises(ValueError, match="Invalid SOLVE-IT data path"):
                    MockSolveItBaseTool(custom_data_path=invalid_path)
    
    def test_resolve_data_path_exception_handling(self, mock_solve_it_environment):
        """Test data path resolution with exception handling."""
        with patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            with patch('solveit_mcp_server.utils.data_path.get_solve_it_data_path', side_effect=Exception("Test error")):
                with pytest.raises(ValueError, match="SOLVE-IT data path resolution failed"):
                    MockSolveItBaseTool()


class TestKnowledgeBaseInitialization:
    """Test knowledge base initialization."""
    
    def test_knowledge_base_initialization_success(self, mock_solve_it_environment):
        """Test successful knowledge base initialization."""
        test_path = "/test/path"
        
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'):
            with patch('sys.path.insert') as mock_sys_path:
                tool = MockSolveItBaseTool()
                tool.data_path = test_path
                tool._init_knowledge_base()
                
                # Verify sys.path.insert was called
                mock_sys_path.assert_called_once_with(0, str(Path(test_path).parent))
                
                # Verify knowledge base was created
                assert hasattr(tool, 'knowledge_base')
                assert tool.knowledge_base is not None
    
    def test_knowledge_base_initialization_failure(self, mock_solve_it_environment):
        """Test knowledge base initialization failure."""
        test_path = "/test/path"
        
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'):
            with patch('sys.path.insert'):
                with patch('solve_it_library.KnowledgeBase', side_effect=Exception("KB Error")):
                    tool = MockSolveItBaseTool()
                    tool.data_path = test_path
                    
                    with pytest.raises(ValueError, match="SOLVE-IT knowledge base initialization failed"):
                        tool._init_knowledge_base()


class TestKnowledgeBaseStats:
    """Test knowledge base statistics functionality."""
    
    def test_get_knowledge_base_stats_success(self, mock_solve_it_environment):
        """Test successful knowledge base stats retrieval."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            tool.data_path = "/test/path"
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            stats = tool.get_knowledge_base_stats()
            
            assert stats['techniques'] == 2
            assert stats['weaknesses'] == 2
            assert stats['mitigations'] == 2
            assert stats['objectives'] == 2
            assert stats['current_mapping'] == "solve-it.json"
            assert stats['data_path'] == "/test/path"
    
    def test_get_knowledge_base_stats_error(self, mock_solve_it_environment):
        """Test knowledge base stats retrieval with error."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.list_techniques.side_effect = Exception("Stats error")
            
            stats = tool.get_knowledge_base_stats()
            
            assert 'error' in stats
            assert stats['error'] == "Stats error"


class TestErrorHandling:
    """Test error handling functionality."""
    
    def test_handle_knowledge_base_error_not_found(self, mock_solve_it_environment):
        """Test handling of 'not found' errors."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            error = Exception("Item not found")
            
            result = tool.handle_knowledge_base_error(error, "test operation")
            
            assert "not found" in result.lower()
            assert "test operation" in result
    
    def test_handle_knowledge_base_error_invalid(self, mock_solve_it_environment):
        """Test handling of 'invalid' errors."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            error = Exception("Invalid input")
            
            result = tool.handle_knowledge_base_error(error, "test operation")
            
            assert "invalid" in result.lower()
            assert "test operation" in result
    
    def test_handle_knowledge_base_error_generic(self, mock_solve_it_environment):
        """Test handling of generic errors."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            error = Exception("Generic error")
            
            result = tool.handle_knowledge_base_error(error, "test operation")
            
            assert "error occurred" in result.lower()
            assert "test operation" in result


class TestToolInvocation:
    """Test tool invocation functionality."""
    
    @pytest.mark.asyncio
    async def test_successful_tool_invocation(self, mock_solve_it_environment):
        """Test successful tool invocation."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            params = MockToolParams(test_param="test_value")
            
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            assert data['test'] == "test_value"
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, mock_solve_it_environment):
        """Test parameter validation in tool invocation."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            
            # Test with valid parameters
            params = MockToolParams(test_param="valid_value")
            result = await tool.invoke(params)
            
            data = validate_json_response(result)
            assert data['test'] == "valid_value"
    
    def test_tool_metadata(self, mock_solve_it_environment):
        """Test tool metadata is properly set."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            
            assert tool.name == "test_tool"
            assert tool.description == "A test tool for unit testing"
            assert tool.Params == MockToolParams
    
    def test_tool_inheritance(self, mock_solve_it_environment):
        """Test that tool properly inherits from SolveItBaseTool."""
        with patch.object(MockSolveItBaseTool, '_resolve_data_path'), \
             patch.object(MockSolveItBaseTool, '_init_knowledge_base'):
            
            tool = MockSolveItBaseTool()
            
            assert isinstance(tool, SolveItBaseTool)
            assert hasattr(tool, 'data_path')
            assert hasattr(tool, 'knowledge_base')
            assert hasattr(tool, 'get_knowledge_base_stats')
            assert hasattr(tool, 'handle_knowledge_base_error')
