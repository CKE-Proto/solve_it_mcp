"""Unit tests for relationship query tools."""

import json
from unittest.mock import patch, MagicMock

import pytest

from solveit_mcp_server.tools.solveit_tools import (
    GetWeaknessesForTechniqueTool,
    GetWeaknessesForTechniqueParams,
    GetMitigationsForWeaknessTool,
    GetMitigationsForWeaknessParams,
    GetTechniquesForWeaknessTool,
    GetTechniquesForWeaknessParams,
    GetWeaknessesForMitigationTool,
    GetWeaknessesForMitigationParams,
    GetTechniquesForMitigationTool,
    GetTechniquesForMitigationParams,
)
from conftest import validate_json_response, assert_error_response


class TestGetWeaknessesForTechniqueTool:
    """Test GetWeaknessesForTechniqueTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetWeaknessesForTechniqueTool()
        
        assert tool.name == "get_weaknesses_for_technique"
        assert "weaknesses associated with" in tool.description.lower()
        assert tool.Params == GetWeaknessesForTechniqueParams
    
    @pytest.mark.asyncio
    async def test_successful_weaknesses_retrieval(self, mock_solve_it_environment):
        """Test successful weaknesses for technique retrieval."""
        with patch.object(GetWeaknessesForTechniqueTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForTechniqueTool, '_init_knowledge_base'):
            
            tool = GetWeaknessesForTechniqueTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetWeaknessesForTechniqueParams(technique_id="T1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "W1001"
            assert data[0]['name'] == "Test Weakness"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_weaknesses_for_technique.assert_called_once_with("T1001")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in weaknesses retrieval."""
        with patch.object(GetWeaknessesForTechniqueTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForTechniqueTool, '_init_knowledge_base'):
            
            tool = GetWeaknessesForTechniqueTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_weaknesses_for_technique.side_effect = Exception("Test error")
            
            params = GetWeaknessesForTechniqueParams(technique_id="T1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetMitigationsForWeaknessTool:
    """Test GetMitigationsForWeaknessTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetMitigationsForWeaknessTool()
        
        assert tool.name == "get_mitigations_for_weakness"
        assert "mitigations associated with" in tool.description.lower()
        assert tool.Params == GetMitigationsForWeaknessParams
    
    @pytest.mark.asyncio
    async def test_successful_mitigations_retrieval(self, mock_solve_it_environment):
        """Test successful mitigations for weakness retrieval."""
        with patch.object(GetMitigationsForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetMitigationsForWeaknessTool, '_init_knowledge_base'):
            
            tool = GetMitigationsForWeaknessTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetMitigationsForWeaknessParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "M1001"
            assert data[0]['name'] == "Test Mitigation"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_mitigations_for_weakness.assert_called_once_with("W1001")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in mitigations retrieval."""
        with patch.object(GetMitigationsForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetMitigationsForWeaknessTool, '_init_knowledge_base'):
            
            tool = GetMitigationsForWeaknessTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_mitigations_for_weakness.side_effect = Exception("Test error")
            
            params = GetMitigationsForWeaknessParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetTechniquesForWeaknessTool:
    """Test GetTechniquesForWeaknessTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetTechniquesForWeaknessTool()
        
        assert tool.name == "get_techniques_for_weakness"
        assert "techniques that reference" in tool.description.lower()
        assert tool.Params == GetTechniquesForWeaknessParams
    
    @pytest.mark.asyncio
    async def test_successful_techniques_retrieval(self, mock_solve_it_environment):
        """Test successful techniques for weakness retrieval."""
        with patch.object(GetTechniquesForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForWeaknessTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForWeaknessTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetTechniquesForWeaknessParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "T1001"
            assert data[0]['name'] == "Test Technique"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_techniques_for_weakness.assert_called_once_with("W1001")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in techniques retrieval."""
        with patch.object(GetTechniquesForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForWeaknessTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForWeaknessTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_techniques_for_weakness.side_effect = Exception("Test error")
            
            params = GetTechniquesForWeaknessParams(weakness_id="W1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetWeaknessesForMitigationTool:
    """Test GetWeaknessesForMitigationTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetWeaknessesForMitigationTool()
        
        assert tool.name == "get_weaknesses_for_mitigation"
        assert "weaknesses that reference" in tool.description.lower()
        assert tool.Params == GetWeaknessesForMitigationParams
    
    @pytest.mark.asyncio
    async def test_successful_weaknesses_retrieval(self, mock_solve_it_environment):
        """Test successful weaknesses for mitigation retrieval."""
        with patch.object(GetWeaknessesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForMitigationTool, '_init_knowledge_base'):
            
            tool = GetWeaknessesForMitigationTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetWeaknessesForMitigationParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "W1001"
            assert data[0]['name'] == "Test Weakness"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_weaknesses_for_mitigation.assert_called_once_with("M1001")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in weaknesses retrieval."""
        with patch.object(GetWeaknessesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForMitigationTool, '_init_knowledge_base'):
            
            tool = GetWeaknessesForMitigationTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_weaknesses_for_mitigation.side_effect = Exception("Test error")
            
            params = GetWeaknessesForMitigationParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestGetTechniquesForMitigationTool:
    """Test GetTechniquesForMitigationTool functionality."""
    
    def test_tool_metadata(self):
        """Test tool metadata is correct."""
        tool = GetTechniquesForMitigationTool()
        
        assert tool.name == "get_techniques_for_mitigation"
        assert "techniques that reference" in tool.description.lower()
        assert tool.Params == GetTechniquesForMitigationParams
    
    @pytest.mark.asyncio
    async def test_successful_techniques_retrieval(self, mock_solve_it_environment):
        """Test successful techniques for mitigation retrieval."""
        with patch.object(GetTechniquesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForMitigationTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForMitigationTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetTechniquesForMitigationParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            # Validate JSON response
            data = validate_json_response(result)
            
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]['id'] == "T1001"
            assert data[0]['name'] == "Test Technique"
            
            # Verify knowledge base method was called correctly
            tool.knowledge_base.get_techniques_for_mitigation.assert_called_once_with("M1001")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_solve_it_environment):
        """Test error handling in techniques retrieval."""
        with patch.object(GetTechniquesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForMitigationTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForMitigationTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.get_techniques_for_mitigation.side_effect = Exception("Test error")
            
            params = GetTechniquesForMitigationParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            assert_error_response(result, "error")


class TestRelationshipToolsIntegration:
    """Test integration between relationship tools."""
    
    @pytest.mark.asyncio
    async def test_forward_relationship_chain(self, mock_solve_it_environment):
        """Test forward relationship chain: technique -> weakness -> mitigation."""
        # Test technique -> weakness
        with patch.object(GetWeaknessesForTechniqueTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForTechniqueTool, '_init_knowledge_base'):
            
            tool1 = GetWeaknessesForTechniqueTool()
            tool1.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params1 = GetWeaknessesForTechniqueParams(technique_id="T1001")
            result1 = await tool1.invoke(params1)
            
            weaknesses = validate_json_response(result1)
            assert len(weaknesses) > 0
            weakness_id = weaknesses[0]['id']
        
        # Test weakness -> mitigation
        with patch.object(GetMitigationsForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetMitigationsForWeaknessTool, '_init_knowledge_base'):
            
            tool2 = GetMitigationsForWeaknessTool()
            tool2.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params2 = GetMitigationsForWeaknessParams(weakness_id=weakness_id)
            result2 = await tool2.invoke(params2)
            
            mitigations = validate_json_response(result2)
            assert len(mitigations) > 0
            assert mitigations[0]['id'] == "M1001"
    
    @pytest.mark.asyncio
    async def test_reverse_relationship_chain(self, mock_solve_it_environment):
        """Test reverse relationship chain: mitigation -> weakness -> technique."""
        # Test mitigation -> weakness
        with patch.object(GetWeaknessesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForMitigationTool, '_init_knowledge_base'):
            
            tool1 = GetWeaknessesForMitigationTool()
            tool1.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params1 = GetWeaknessesForMitigationParams(mitigation_id="M1001")
            result1 = await tool1.invoke(params1)
            
            weaknesses = validate_json_response(result1)
            assert len(weaknesses) > 0
            weakness_id = weaknesses[0]['id']
        
        # Test weakness -> technique
        with patch.object(GetTechniquesForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForWeaknessTool, '_init_knowledge_base'):
            
            tool2 = GetTechniquesForWeaknessTool()
            tool2.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params2 = GetTechniquesForWeaknessParams(weakness_id=weakness_id)
            result2 = await tool2.invoke(params2)
            
            techniques = validate_json_response(result2)
            assert len(techniques) > 0
            assert techniques[0]['id'] == "T1001"
    
    @pytest.mark.asyncio
    async def test_direct_mitigation_to_technique_lookup(self, mock_solve_it_environment):
        """Test direct mitigation to technique lookup."""
        with patch.object(GetTechniquesForMitigationTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForMitigationTool, '_init_knowledge_base'):
            
            tool = GetTechniquesForMitigationTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            params = GetTechniquesForMitigationParams(mitigation_id="M1001")
            result = await tool.invoke(params)
            
            techniques = validate_json_response(result)
            assert len(techniques) > 0
            assert techniques[0]['id'] == "T1001"
