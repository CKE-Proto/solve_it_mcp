"""Unit tests for objective and mapping management tools."""

import json
from unittest.mock import patch, MagicMock

import pytest

from solveit_mcp_server.tools.solveit_tools import (
    ListObjectivesTool,
    ListObjectivesParams,
    GetTechniquesForObjectiveTool,
    GetTechniquesForObjectiveParams,
    ListAvailableMappingsTool,
    ListAvailableMappingsParams,
    LoadObjectiveMappingTool,
    LoadObjectiveMappingParams,
)
from conftest import validate_json_response, assert_error_response


class TestListObjectivesTool:
    """Test ListObjectivesTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = ListObjectivesTool()
        
        assert tool.name == "list_objectives"
        assert "objectives from the current" in tool.description.lower()
        assert tool.Params == ListObjectivesParams
    
    @pytest.mark.asyncio
    async def test_successful_objectives_listing(self, mock_solve_it_environment):
        """Test successful objectives listing."""
        with patch.object(ListObjectivesTool, '_resolve_data_path'), \
             patch.object(ListObjectivesTool, '_init_knowledge_base'):
            
            tool = ListObjectivesTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = ListObjectivesParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert "Test Objective 1" in data
            assert "Test Objective 2" in data
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.list_objectives.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in objectives listing."""
        with patch.object(ListObjectivesTool, '_resolve_data_path'), \
             patch.object(ListObjectivesTool, '_init_knowledge_base'):
            
            tool = ListObjectivesTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.list_objectives.side_effect = Exception("Test error")
            
            params = ListObjectivesParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetTechniquesForObjectiveTool:
    """Test GetTechniquesForObjectiveTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetTechniquesForObjectiveTool()
        
        assert tool.name == "get_techniques_for_objective"
        assert "techniques associated with" in tool.description.lower()
        assert tool.Params == GetTechniquesForObjectiveParams
    
    @pytest.mark.asyncio
    async def test_successful_techniques_retrieval(self, mock_solve_it_environment):
        """Test successful techniques for objective retrieval."""
        with patch.object(GetTechniquesForObjectiveTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForObjectiveTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForObjectiveTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetTechniquesForObjectiveParams(objective_name="Test Objective 1")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "T1001"
            assert data[0]['name'] == "Test Technique"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_techniques_for_objective.assert_called_once_with("Test Objective 1")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in techniques retrieval."""
        with patch.object(GetTechniquesForObjectiveTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForObjectiveTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForObjectiveTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_techniques_for_objective.side_effect = Exception("Test error")
            
            params = GetTechniquesForObjectiveParams(objective_name="Test Objective")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestListAvailableMappingsTool:
    """Test ListAvailableMappingsTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = ListAvailableMappingsTool()
        
        assert tool.name == "list_available_mappings"
        assert "available" in tool.description.lower()
        assert "mapping" in tool.description.lower()
        assert tool.Params == ListAvailableMappingsParams
    
    @pytest.mark.asyncio
    async def test_successful_mappings_listing(self, mock_solve_it_environment):
        """Test successful mappings listing."""
        with patch.object(ListAvailableMappingsTool, '_resolve_data_path'), \
             patch.object(ListAvailableMappingsTool, '_init_knowledge_base'):
            
            tool = ListAvailableMappingsTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = ListAvailableMappingsParams()
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) == 2
            assert "solve-it.json" in data
            assert "carrier.json" in data
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.list_available_mappings.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in mappings listing."""
        with patch.object(ListAvailableMappingsTool, '_resolve_data_path'), \
             patch.object(ListAvailableMappingsTool, '_init_knowledge_base'):
            
            tool = ListAvailableMappingsTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.list_available_mappings.side_effect = Exception("Test error")
            
            params = ListAvailableMappingsParams()
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestLoadObjectiveMappingTool:
    """Test LoadObjectiveMappingTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = LoadObjectiveMappingTool()
        
        assert tool.name == "load_objective_mapping"
        assert "switches to a different" in tool.description.lower()
        assert tool.Params == LoadObjectiveMappingParams
    
    @pytest.mark.asyncio
    async def test_successful_mapping_load(self, mock_solve_it_environment):
        """Test successful mapping load."""
        with patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            tool = LoadObjectiveMappingTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = LoadObjectiveMappingParams(filename="carrier.json")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['success'] is True
            assert data['message'] == "Successfully loaded mapping: carrier.json"
            assert data['current_mapping'] == "carrier.json"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.load_objective_mapping.assert_called_once_with("carrier.json")
    
    @pytest.mark.asyncio
    async def test_failed_mapping_load(self, mock_solve_it_environment):
        """Test failed mapping load."""
        with patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            tool = LoadObjectiveMappingTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            tool.knowledge_base.load_objective_mapping.return_value = False
            
            params = LoadObjectiveMappingParams(filename="nonexistent.json")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert data['success'] is False
            assert data['message'] == "Failed to load mapping: nonexistent.json"
            assert data['current_mapping'] == "solve-it.json"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.load_objective_mapping.assert_called_once_with("nonexistent.json")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in mapping load."""
        with patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            tool = LoadObjectiveMappingTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.load_objective_mapping.side_effect = Exception("Test error")
            
            params = LoadObjectiveMappingParams(filename="test.json")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestObjectiveToolsIntegration:
    """Test integration between objective tools."""
    
    @pytest.mark.asyncio
    async def test_objective_workflow(self, mock_solve_it_environment):
        """Test complete objective workflow: list -> select -> get techniques."""
        # Step 1: List available objectives
        with patch.object(ListObjectivesTool, '_resolve_data_path'), \
             patch.object(ListObjectivesTool, '_init_knowledge_base'):
            
            tool1 = ListObjectivesTool()
            tool1.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params1 = ListObjectivesParams()
            result1 = await tool1.invoke(params1)
            
            objectives = validate_json_response(result1)
            assert len(objectives) > 0
            objective_name = objectives[0]
        
        # Step 2: Get techniques for selected objective
        with patch.object(GetTechniquesForObjectiveTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForObjectiveTool, '_init_knowledge_base'):
            
            tool2 = GetTechniquesForObjectiveTool()
            tool2.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params2 = GetTechniquesForObjectiveParams(objective_name=objective_name)
            result2 = await tool2.invoke(params2)
            
            techniques = validate_json_response(result2)
            assert len(techniques) > 0
            assert techniques[0]['id'] == "T1001"
    
    @pytest.mark.asyncio
    async def test_mapping_workflow(self, mock_solve_it_environment):
        """Test complete mapping workflow: list -> load -> list objectives."""
        # Step 1: List available mappings
        with patch.object(ListAvailableMappingsTool, '_resolve_data_path'), \
             patch.object(ListAvailableMappingsTool, '_init_knowledge_base'):
            
            tool1 = ListAvailableMappingsTool()
            tool1.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params1 = ListAvailableMappingsParams()
            result1 = await tool1.invoke(params1)
            
            mappings = validate_json_response(result1)
            assert len(mappings) > 0
            assert "carrier.json" in mappings
        
        # Step 2: Load a different mapping
        with patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            tool2 = LoadObjectiveMappingTool()
            tool2.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params2 = LoadObjectiveMappingParams(filename="carrier.json")
            result2 = await tool2.invoke(params2)
            
            load_result = validate_json_response(result2)
            assert load_result['success'] is True
        
        # Step 3: List objectives from new mapping
        with patch.object(ListObjectivesTool, '_resolve_data_path'), \
             patch.object(ListObjectivesTool, '_init_knowledge_base'):
            
            tool3 = ListObjectivesTool()
            tool3.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params3 = ListObjectivesParams()
            result3 = await tool3.invoke(params3)
            
            objectives = validate_json_response(result3)
            assert len(objectives) > 0
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, mock_solve_it_environment):
        """Test parameter validation for objective tools."""
        # Test GetTechniquesForObjectiveParams validation
        with patch.object(GetTechniquesForObjectiveTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForObjectiveTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForObjectiveTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            # Valid parameter
            params = GetTechniquesForObjectiveParams(objective_name="Valid Objective")
            result = await tool.invoke(params)
            
            # Should not raise validation error
            validate_json_response(result)
        
        # Test LoadObjectiveMappingParams validation
        with patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            tool = LoadObjectiveMappingTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            # Valid parameter
            params = LoadObjectiveMappingParams(filename="valid.json")
            result = await tool.invoke(params)
            
            # Should not raise validation error
            validate_json_response(result)
