"""Unit tests for bulk retrieval tools."""

import json
from unittest.mock import patch, MagicMock

import pytest

from solveit_mcp_server.tools.solveit_tools import (
    GetAllTechniquesWithNameAndIdTool,
    GetAllTechniquesWithNameAndIdParams,
    GetAllWeaknessesWithNameAndIdTool,
    GetAllWeaknessesWithNameAndIdParams,
    GetAllMitigationsWithNameAndIdTool,
    GetAllMitigationsWithNameAndIdParams,
    GetAllTechniquesWithFullDetailTool,
    GetAllTechniquesWithFullDetailParams,
    GetAllWeaknessesWithFullDetailTool,
    GetAllWeaknessesWithFullDetailParams,
    GetAllMitigationsWithFullDetailTool,
    GetAllMitigationsWithFullDetailParams,
)
from conftest import validate_json_response, assert_error_response


class TestGetAllTechniquesWithNameAndIdTool:
    """Test GetAllTechniquesWithNameAndIdTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllTechniquesWithNameAndIdTool()
        
        assert tool.name == "get_all_techniques_with_name_and_id"
        assert "concise format" in tool.description.lower()
        assert tool.Params == GetAllTechniquesWithNameAndIdParams
    
    @pytest.mark.asyncio
    async def test_successful_techniques_retrieval(self, mock_solve_it_environment):
        """Test successful techniques retrieval."""
        with patch.object(GetAllTechniquesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllTechniquesWithNameAndIdTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllTechniquesWithNameAndIdParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['id'] == "T1001"
            assert data[0]['name'] == "Test Technique 1"
            assert data[1]['id'] == "T1002"
            assert data[1]['name'] == "Test Technique 2"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_techniques_with_name_and_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in techniques retrieval."""
        with patch.object(GetAllTechniquesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllTechniquesWithNameAndIdTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_techniques_with_name_and_id.side_effect = Exception("Test error")
            
            params = GetAllTechniquesWithNameAndIdParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetAllWeaknessesWithNameAndIdTool:
    """Test GetAllWeaknessesWithNameAndIdTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllWeaknessesWithNameAndIdTool()
        
        assert tool.name == "get_all_weaknesses_with_name_and_id"
        assert "concise format" in tool.description.lower()
        assert tool.Params == GetAllWeaknessesWithNameAndIdParams
    
    @pytest.mark.asyncio
    async def test_successful_weaknesses_retrieval(self, mock_solve_it_environment):
        """Test successful weaknesses retrieval."""
        with patch.object(GetAllWeaknessesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllWeaknessesWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllWeaknessesWithNameAndIdTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllWeaknessesWithNameAndIdParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['id'] == "W1001"
            assert data[0]['name'] == "Test Weakness 1"
            assert data[1]['id'] == "W1002"
            assert data[1]['name'] == "Test Weakness 2"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_weaknesses_with_name_and_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in weaknesses retrieval."""
        with patch.object(GetAllWeaknessesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllWeaknessesWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllWeaknessesWithNameAndIdTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_weaknesses_with_name_and_id.side_effect = Exception("Test error")
            
            params = GetAllWeaknessesWithNameAndIdParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetAllMitigationsWithNameAndIdTool:
    """Test GetAllMitigationsWithNameAndIdTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllMitigationsWithNameAndIdTool()
        
        assert tool.name == "get_all_mitigations_with_name_and_id"
        assert "concise format" in tool.description.lower()
        assert tool.Params == GetAllMitigationsWithNameAndIdParams
    
    @pytest.mark.asyncio
    async def test_successful_mitigations_retrieval(self, mock_solve_it_environment):
        """Test successful mitigations retrieval."""
        with patch.object(GetAllMitigationsWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllMitigationsWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllMitigationsWithNameAndIdTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllMitigationsWithNameAndIdParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]['id'] == "M1001"
            assert data[0]['name'] == "Test Mitigation 1"
            assert data[1]['id'] == "M1002"
            assert data[1]['name'] == "Test Mitigation 2"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_mitigations_with_name_and_id.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in mitigations retrieval."""
        with patch.object(GetAllMitigationsWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllMitigationsWithNameAndIdTool, '_init_knowledge_base'):
            
            tool = GetAllMitigationsWithNameAndIdTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_mitigations_with_name_and_id.side_effect = Exception("Test error")
            
            params = GetAllMitigationsWithNameAndIdParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetAllTechniquesWithFullDetailTool:
    """Test GetAllTechniquesWithFullDetailTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllTechniquesWithFullDetailTool()
        
        assert tool.name == "get_all_techniques_with_full_detail"
        assert "complete details" in tool.description.lower()
        assert "warning" in tool.description.lower()
        assert tool.Params == GetAllTechniquesWithFullDetailParams
    
    @pytest.mark.asyncio
    async def test_successful_techniques_retrieval(self, mock_solve_it_environment):
        """Test successful techniques retrieval with full details."""
        with patch.object(GetAllTechniquesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllTechniquesWithFullDetailTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllTechniquesWithFullDetailParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['id'] == "T1001"
            assert data[0]['name'] == "Test Technique"
            assert 'description' in data[0]
            assert 'weaknesses' in data[0]
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_techniques_with_full_detail.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in techniques retrieval."""
        with patch.object(GetAllTechniquesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllTechniquesWithFullDetailTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_techniques_with_full_detail.side_effect = Exception("Test error")
            
            params = GetAllTechniquesWithFullDetailParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetAllWeaknessesWithFullDetailTool:
    """Test GetAllWeaknessesWithFullDetailTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllWeaknessesWithFullDetailTool()
        
        assert tool.name == "get_all_weaknesses_with_full_detail"
        assert "complete details" in tool.description.lower()
        assert "warning" in tool.description.lower()
        assert tool.Params == GetAllWeaknessesWithFullDetailParams
    
    @pytest.mark.asyncio
    async def test_successful_weaknesses_retrieval(self, mock_solve_it_environment):
        """Test successful weaknesses retrieval with full details."""
        with patch.object(GetAllWeaknessesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllWeaknessesWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllWeaknessesWithFullDetailTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllWeaknessesWithFullDetailParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['id'] == "W1001"
            assert data[0]['name'] == "Test Weakness"
            assert 'description' in data[0]
            assert 'mitigations' in data[0]
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_weaknesses_with_full_detail.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in weaknesses retrieval."""
        with patch.object(GetAllWeaknessesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllWeaknessesWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllWeaknessesWithFullDetailTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_weaknesses_with_full_detail.side_effect = Exception("Test error")
            
            params = GetAllWeaknessesWithFullDetailParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetAllMitigationsWithFullDetailTool:
    """Test GetAllMitigationsWithFullDetailTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetAllMitigationsWithFullDetailTool()
        
        assert tool.name == "get_all_mitigations_with_full_detail"
        assert "complete details" in tool.description.lower()
        assert "warning" in tool.description.lower()
        assert tool.Params == GetAllMitigationsWithFullDetailParams
    
    @pytest.mark.asyncio
    async def test_successful_mitigations_retrieval(self, mock_solve_it_environment):
        """Test successful mitigations retrieval with full details."""
        with patch.object(GetAllMitigationsWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllMitigationsWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllMitigationsWithFullDetailTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetAllMitigationsWithFullDetailParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]['id'] == "M1001"
            assert data[0]['name'] == "Test Mitigation"
            assert 'description' in data[0]
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_all_mitigations_with_full_detail.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in mitigations retrieval."""
        with patch.object(GetAllMitigationsWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllMitigationsWithFullDetailTool, '_init_knowledge_base'):
            
            tool = GetAllMitigationsWithFullDetailTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_all_mitigations_with_full_detail.side_effect = Exception("Test error")
            
            params = GetAllMitigationsWithFullDetailParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestBulkToolsPerformance:
    """Test performance characteristics of bulk tools."""
    
    @pytest.mark.asyncio
    async def test_concise_vs_full_detail_performance(self, mock_solve_it_environment):
        """Test that concise format tools are faster than full detail tools."""
        # This test verifies that the tools call the correct methods
        # Performance testing would need real data and timing
        
        # Test concise format
        with patch.object(GetAllTechniquesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_init_knowledge_base'):
            
            tool_concise = GetAllTechniquesWithNameAndIdTool()
            tool_concise.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params_concise = GetAllTechniquesWithNameAndIdParams()
            result_concise = await tool_concise.invoke(params_concise)
            
            # Validate concise response
            data_concise = validate_json_response(result_concise)
            assert len(data_concise) == 2
            assert 'id' in data_concise[0]
            assert 'name' in data_concise[0]
            # Should not have full details
            assert 'description' not in data_concise[0]
        
        # Test full detail format
        with patch.object(GetAllTechniquesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithFullDetailTool, '_init_knowledge_base'):
            
            tool_full = GetAllTechniquesWithFullDetailTool()
            tool_full.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params_full = GetAllTechniquesWithFullDetailParams()
            result_full = await tool_full.invoke(params_full)
            
            # Validate full response
            data_full = validate_json_response(result_full)
            assert len(data_full) == 1
            assert 'id' in data_full[0]
            assert 'name' in data_full[0]
            # Should have full details
            assert 'description' in data_full[0]
    
    @pytest.mark.asyncio
    async def test_bulk_tools_consistency(self, mock_solve_it_environment):
        """Test that bulk tools return consistent data structures."""
        # Test all concise format tools
        concise_tools = [
            (GetAllTechniquesWithNameAndIdTool, GetAllTechniquesWithNameAndIdParams),
            (GetAllWeaknessesWithNameAndIdTool, GetAllWeaknessesWithNameAndIdParams),
            (GetAllMitigationsWithNameAndIdTool, GetAllMitigationsWithNameAndIdParams),
        ]
        
        for tool_class, params_class in concise_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                
                tool = tool_class()
                tool.knowledge_base = mock_solve_it_environment['knowledge_base']
                
                params = params_class()
                result = await tool.invoke(params)
                
                # Validate consistent structure
                data = validate_json_response(result)
                assert isinstance(data, list)
                if len(data) > 0:
                    assert 'id' in data[0]
                    assert 'name' in data[0]
                    assert len(data[0]) == 2  # Only id and name
        
        # Test all full detail tools
        full_tools = [
            (GetAllTechniquesWithFullDetailTool, GetAllTechniquesWithFullDetailParams),
            (GetAllWeaknessesWithFullDetailTool, GetAllWeaknessesWithFullDetailParams),
            (GetAllMitigationsWithFullDetailTool, GetAllMitigationsWithFullDetailParams),
        ]
        
        for tool_class, params_class in full_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                
                tool = tool_class()
                tool.knowledge_base = mock_solve_it_environment['knowledge_base']
                
                params = params_class()
                result = await tool.invoke(params)
                
                # Validate consistent structure
                data = validate_json_response(result)
                assert isinstance(data, list)
                if len(data) > 0:
                    assert 'id' in data[0]
                    assert 'name' in data[0]
                    assert 'description' in data[0]
                    assert len(data[0]) > 2  # More than just id and name
