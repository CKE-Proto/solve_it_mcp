"""Unit tests for essential query tools."""

import json
from unittest.mock import patch, MagicMock

import pytest

from solveit_mcp_server.tools.solveit_tools import (
    GetDatabaseDescriptionTool,
    GetDatabaseDescriptionParams,
    SearchTool,
    SearchParams,
    GetTechniqueDetailsTool,
    GetTechniqueDetailsParams,
    GetWeaknessDetailsTool,
    GetWeaknessDetailsParams,
    GetMitigationDetailsTool,
    GetMitigationDetailsParams,
)
from conftest import validate_json_response, assert_error_response


class TestGetDatabaseDescriptionTool:
    """Test GetDatabaseDescriptionTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetDatabaseDescriptionTool()
        
        assert tool.name == "get_database_description"
        assert "comprehensive description" in tool.description
        assert tool.Params == GetDatabaseDescriptionParams
    
    @pytest.mark.asyncio
    async def test_successful_invocation(self, mock_solve_it_environment):
        """Test successful database description retrieval."""
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
            
            tool = GetDatabaseDescriptionTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            tool.data_path = "/test/path"
            
            params = GetDatabaseDescriptionParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['database_name'] == "SOLVE-IT Digital Forensics Knowledge Base"
            assert 'description' in data
            assert 'statistics' in data
            assert 'mcp_server_role' in data
            assert 'available_operations' in data
            
            # Check statistics
            stats = data['statistics']
            assert stats['techniques'] == 2
            assert stats['weaknesses'] == 2
            assert stats['mitigations'] == 2
            assert stats['objectives'] == 2
            assert stats['current_mapping'] == "solve-it.json"
            assert stats['data_path'] == "/test/path"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in database description retrieval."""
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
            
            tool = GetDatabaseDescriptionTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.list_techniques.side_effect = Exception("Test error")
            
            params = GetDatabaseDescriptionParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestSearchTool:
    """Test SearchTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = SearchTool()
        
        assert tool.name == "search"
        assert "searches the knowledge base" in tool.description.lower()
        assert tool.Params == SearchParams
    
    @pytest.mark.asyncio
    async def test_successful_search_all_types(self, mock_solve_it_environment):
        """Test successful search across all item types."""
        with patch.object(SearchTool, '_resolve_data_path'), \
             patch.object(SearchTool, '_init_knowledge_base'):
            
            tool = SearchTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = SearchParams(keywords="test search")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert 'techniques' in data
            assert 'weaknesses' in data
            assert 'mitigations' in data
            
            # Verify knowledge base search was called correctly
            tool.knowledge_base.search.assert_called_once_with(
                keywords="test search",
                item_types=None
            )
    
    @pytest.mark.asyncio
    async def test_search_specific_item_types(self, mock_solve_it_environment):
        """Test search with specific item types."""
        with patch.object(SearchTool, '_resolve_data_path'), \
             patch.object(SearchTool, '_init_knowledge_base'):
            
            tool = SearchTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = SearchParams(keywords="test", item_types=["techniques", "weaknesses"])
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            # Verify knowledge base search was called correctly
            tool.knowledge_base.search.assert_called_once_with(
                keywords="test",
                item_types=["techniques", "weaknesses"]
            )
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, mock_solve_it_environment):
        """Test error handling in search."""
        with patch.object(SearchTool, '_resolve_data_path'), \
             patch.object(SearchTool, '_init_knowledge_base'):
            
            tool = SearchTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.search.side_effect = Exception("Search error")
            
            params = SearchParams(keywords="test")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetTechniqueDetailsTool:
    """Test GetTechniqueDetailsTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetTechniqueDetailsTool()
        
        assert tool.name == "get_technique_details"
        assert "technique" in tool.description.lower()
        assert tool.Params == GetTechniqueDetailsParams
    
    @pytest.mark.asyncio
    async def test_successful_technique_retrieval(self, mock_solve_it_environment):
        """Test successful technique details retrieval."""
        with patch.object(GetTechniqueDetailsTool, '_resolve_data_path'), \
             patch.object(GetTechniqueDetailsTool, '_init_knowledge_base'):
            
            tool = GetTechniqueDetailsTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetTechniqueDetailsParams(technique_id="T1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['id'] == "T1001"
            assert data['name'] == "Test Technique"
            assert 'description' in data
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_technique.assert_called_once_with("T1001")
    
    @pytest.mark.asyncio
    async def test_technique_not_found(self, mock_solve_it_environment):
        """Test handling of technique not found."""
        with patch.object(GetTechniqueDetailsTool, '_resolve_data_path'), \
             patch.object(GetTechniqueDetailsTool, '_init_knowledge_base'):
            
            tool = GetTechniqueDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_technique.return_value = None
            
            params = GetTechniqueDetailsParams(technique_id="T9999")
            result = await tool.invoke(params)
            
            assert "T9999 not found" in result
    
    @pytest.mark.asyncio
    async def test_technique_error_handling(self, mock_solve_it_environment):
        """Test error handling in technique retrieval."""
        with patch.object(GetTechniqueDetailsTool, '_resolve_data_path'), \
             patch.object(GetTechniqueDetailsTool, '_init_knowledge_base'):
            
            tool = GetTechniqueDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_technique.side_effect = Exception("Technique error")
            
            params = GetTechniqueDetailsParams(technique_id="T1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetWeaknessDetailsTool:
    """Test GetWeaknessDetailsTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetWeaknessDetailsTool()
        
        assert tool.name == "get_weakness_details"
        assert "weakness" in tool.description.lower()
        assert tool.Params == GetWeaknessDetailsParams
    
    @pytest.mark.asyncio
    async def test_successful_weakness_retrieval(self, mock_solve_it_environment):
        """Test successful weakness details retrieval."""
        with patch.object(GetWeaknessDetailsTool, '_resolve_data_path'), \
             patch.object(GetWeaknessDetailsTool, '_init_knowledge_base'):
            
            tool = GetWeaknessDetailsTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetWeaknessDetailsParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['id'] == "W1001"
            assert data['name'] == "Test Weakness"
            assert 'description' in data
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_weakness.assert_called_once_with("W1001")
    
    @pytest.mark.asyncio
    async def test_weakness_not_found(self, mock_solve_it_environment):
        """Test handling of weakness not found."""
        with patch.object(GetWeaknessDetailsTool, '_resolve_data_path'), \
             patch.object(GetWeaknessDetailsTool, '_init_knowledge_base'):
            
            tool = GetWeaknessDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_weakness.return_value = None
            
            params = GetWeaknessDetailsParams(weakness_id="W9999")
            result = await tool.invoke(params)
            
            assert "W9999 not found" in result
    
    @pytest.mark.asyncio
    async def test_weakness_error_handling(self, mock_solve_it_environment):
        """Test error handling in weakness retrieval."""
        with patch.object(GetWeaknessDetailsTool, '_resolve_data_path'), \
             patch.object(GetWeaknessDetailsTool, '_init_knowledge_base'):
            
            tool = GetWeaknessDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_weakness.side_effect = Exception("Weakness error")
            
            params = GetWeaknessDetailsParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetMitigationDetailsTool:
    """Test GetMitigationDetailsTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetMitigationDetailsTool()
        
        assert tool.name == "get_mitigation_details"
        assert "mitigation" in tool.description.lower()
        assert tool.Params == GetMitigationDetailsParams
    
    @pytest.mark.asyncio
    async def test_successful_mitigation_retrieval(self, mock_solve_it_environment):
        """Test successful mitigation details retrieval."""
        with patch.object(GetMitigationDetailsTool, '_resolve_data_path'), \
             patch.object(GetMitigationDetailsTool, '_init_knowledge_base'):
            
            tool = GetMitigationDetailsTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetMitigationDetailsParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['id'] == "M1001"
            assert data['name'] == "Test Mitigation"
            assert 'description' in data
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_mitigation.assert_called_once_with("M1001")
    
    @pytest.mark.asyncio
    async def test_mitigation_not_found(self, mock_solve_it_environment):
        """Test handling of mitigation not found."""
        with patch.object(GetMitigationDetailsTool, '_resolve_data_path'), \
             patch.object(GetMitigationDetailsTool, '_init_knowledge_base'):
            
            tool = GetMitigationDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_mitigation.return_value = None
            
            params = GetMitigationDetailsParams(mitigation_id="M9999")
            result = await tool.invoke(params)
            
            assert "M9999 not found" in result
    
    @pytest.mark.asyncio
    async def test_mitigation_error_handling(self, mock_solve_it_environment):
        """Test error handling in mitigation retrieval."""
        with patch.object(GetMitigationDetailsTool, '_resolve_data_path'), \
             patch.object(GetMitigationDetailsTool, '_init_knowledge_base'):
            
            tool = GetMitigationDetailsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_mitigation.side_effect = Exception("Mitigation error")
            
            params = GetMitigationDetailsParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")
