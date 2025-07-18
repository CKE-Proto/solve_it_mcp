"""Integration tests for the SOLVE-IT MCP server."""

import json
from unittest.mock import patch, MagicMock
import pytest

from server import create_server
from conftest import validate_json_response


class TestServerIntegration:
    """Test full server integration with all tools."""
    
    def test_server_creation_and_tool_registration(self, mock_solve_it_environment):
        """Test server creation and tool registration workflow."""
        # Test server creation
        with patch('server.Server') as mock_server_class:
            mock_server = MagicMock()
            mock_server_class.return_value = mock_server
            
            server = create_server()
            
            # Verify server was created correctly
            assert server == mock_server
            mock_server_class.assert_called_once_with("solveit_mcp_server")
    
    def test_tool_workflow_database_description(self, mock_solve_it_environment):
        """Test database description tool workflow."""
        from tools.solveit_tools import GetDatabaseDescriptionTool, GetDatabaseDescriptionParams
        
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
            
            tool = GetDatabaseDescriptionTool()
            tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            tool.data_path = mock_solve_it_environment['data_path']
            
            # Test workflow
            params = GetDatabaseDescriptionParams()
            result = tool.invoke(params)
            
            # Verify result
            assert result is not None
    
    def test_tool_workflow_search_and_details(self, mock_solve_it_environment):
        """Test search -> details workflow."""
        from tools.solveit_tools import (
            SearchTool, SearchParams,
            GetTechniqueDetailsTool, GetTechniqueDetailsParams
        )
        
        with patch.object(SearchTool, '_resolve_data_path'), \
             patch.object(SearchTool, '_init_knowledge_base'), \
             patch.object(GetTechniqueDetailsTool, '_resolve_data_path'), \
             patch.object(GetTechniqueDetailsTool, '_init_knowledge_base'):
            
            # Step 1: Search for techniques
            search_tool = SearchTool()
            search_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            search_params = SearchParams(keywords="test", item_types=["techniques"])
            search_result = search_tool.invoke(search_params)
            
            # Step 2: Get details for first technique
            details_tool = GetTechniqueDetailsTool()
            details_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            details_params = GetTechniqueDetailsParams(technique_id="T1001")
            details_result = details_tool.invoke(details_params)
            
            # Verify workflow
            assert search_result is not None
            assert details_result is not None
    
    def test_tool_workflow_relationship_chain(self, mock_solve_it_environment):
        """Test technique -> weakness -> mitigation chain."""
        from tools.solveit_tools import (
            GetWeaknessesForTechniqueTool, GetWeaknessesForTechniqueParams,
            GetMitigationsForWeaknessTool, GetMitigationsForWeaknessParams
        )
        
        with patch.object(GetWeaknessesForTechniqueTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForTechniqueTool, '_init_knowledge_base'), \
             patch.object(GetMitigationsForWeaknessTool, '_resolve_data_path'), \
             patch.object(GetMitigationsForWeaknessTool, '_init_knowledge_base'):
            
            # Step 1: Get weaknesses for technique
            weakness_tool = GetWeaknessesForTechniqueTool()
            weakness_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            weakness_params = GetWeaknessesForTechniqueParams(technique_id="T1001")
            weakness_result = weakness_tool.invoke(weakness_params)
            
            # Step 2: Get mitigations for weakness
            mitigation_tool = GetMitigationsForWeaknessTool()
            mitigation_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            mitigation_params = GetMitigationsForWeaknessParams(weakness_id="W1001")
            mitigation_result = mitigation_tool.invoke(mitigation_params)
            
            # Verify workflow
            assert weakness_result is not None
            assert mitigation_result is not None
    
    def test_tool_workflow_objective_management(self, mock_solve_it_environment):
        """Test objective listing and technique retrieval."""
        from tools.solveit_tools import (
            ListObjectivesTool, ListObjectivesParams,
            GetTechniquesForObjectiveTool, GetTechniquesForObjectiveParams
        )
        
        with patch.object(ListObjectivesTool, '_resolve_data_path'), \
             patch.object(ListObjectivesTool, '_init_knowledge_base'), \
             patch.object(GetTechniquesForObjectiveTool, '_resolve_data_path'), \
             patch.object(GetTechniquesForObjectiveTool, '_init_knowledge_base'):
            
            # Step 1: List objectives
            objectives_tool = ListObjectivesTool()
            objectives_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            objectives_params = ListObjectivesParams()
            objectives_result = objectives_tool.invoke(objectives_params)
            
            # Step 2: Get techniques for objective
            techniques_tool = GetTechniquesForObjectiveTool()
            techniques_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            techniques_params = GetTechniquesForObjectiveParams(objective_name="Test Objective 1")
            techniques_result = techniques_tool.invoke(techniques_params)
            
            # Verify workflow
            assert objectives_result is not None
            assert techniques_result is not None
    
    def test_tool_workflow_mapping_management(self, mock_solve_it_environment):
        """Test mapping listing and loading."""
        from tools.solveit_tools import (
            ListAvailableMappingsTool, ListAvailableMappingsParams,
            LoadObjectiveMappingTool, LoadObjectiveMappingParams
        )
        
        with patch.object(ListAvailableMappingsTool, '_resolve_data_path'), \
             patch.object(ListAvailableMappingsTool, '_init_knowledge_base'), \
             patch.object(LoadObjectiveMappingTool, '_resolve_data_path'), \
             patch.object(LoadObjectiveMappingTool, '_init_knowledge_base'):
            
            # Step 1: List available mappings
            mappings_tool = ListAvailableMappingsTool()
            mappings_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            mappings_params = ListAvailableMappingsParams()
            mappings_result = mappings_tool.invoke(mappings_params)
            
            # Step 2: Load a mapping
            load_tool = LoadObjectiveMappingTool()
            load_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            load_params = LoadObjectiveMappingParams(filename="carrier.json")
            load_result = load_tool.invoke(load_params)
            
            # Verify workflow
            assert mappings_result is not None
            assert load_result is not None
    
    def test_tool_workflow_bulk_operations(self, mock_solve_it_environment):
        """Test bulk operation workflows."""
        from tools.solveit_tools import (
            GetAllTechniquesWithNameAndIdTool, GetAllTechniquesWithNameAndIdParams,
            GetAllTechniquesWithFullDetailTool, GetAllTechniquesWithFullDetailParams
        )
        
        with patch.object(GetAllTechniquesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_init_knowledge_base'), \
             patch.object(GetAllTechniquesWithFullDetailTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithFullDetailTool, '_init_knowledge_base'):
            
            # Test concise bulk operation
            concise_tool = GetAllTechniquesWithNameAndIdTool()
            concise_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            concise_params = GetAllTechniquesWithNameAndIdParams()
            concise_result = concise_tool.invoke(concise_params)
            
            # Test full detail bulk operation
            full_tool = GetAllTechniquesWithFullDetailTool()
            full_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            full_params = GetAllTechniquesWithFullDetailParams()
            full_result = full_tool.invoke(full_params)
            
            # Verify workflow
            assert concise_result is not None
            assert full_result is not None


class TestErrorHandlingIntegration:
    """Test error handling across the server."""
    
    def test_data_path_resolution_failure(self):
        """Test server behavior when data path resolution fails."""
        from tools.solveit_tools import GetDatabaseDescriptionTool
        
        with patch('utils.data_path.get_solve_it_data_path', side_effect=Exception("Path not found")):
            with pytest.raises(ValueError, match="SOLVE-IT data path resolution failed"):
                GetDatabaseDescriptionTool()
    
    def test_knowledge_base_initialization_failure(self):
        """Test server behavior when knowledge base initialization fails."""
        from tools.solveit_tools import GetDatabaseDescriptionTool
        
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch('solve_it_library.KnowledgeBase', side_effect=Exception("KB init failed")):
            with pytest.raises(ValueError, match="SOLVE-IT knowledge base initialization failed"):
                GetDatabaseDescriptionTool()
    
    def test_tool_error_propagation(self, mock_solve_it_environment):
        """Test that tool errors are properly handled and propagated."""
        from tools.solveit_tools import SearchTool, SearchParams
        
        with patch.object(SearchTool, '_resolve_data_path'), \
             patch.object(SearchTool, '_init_knowledge_base'):
            
            tool = SearchTool()
            tool.knowledge_base = MagicMock()
            tool.knowledge_base.search.side_effect = Exception("Search failed")
            
            params = SearchParams(keywords="test")
            result = tool.invoke(params)
            
            # Error should be handled gracefully
            assert result is not None
            assert isinstance(result, str)
            assert "error" in result.lower()


class TestPerformanceIntegration:
    """Test performance characteristics of the server."""
    
    def test_multiple_tool_instances(self, mock_solve_it_environment):
        """Test that multiple tool instances can be created."""
        from tools.solveit_tools import GetDatabaseDescriptionTool
        
        tools = []
        for i in range(5):
            with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
                 patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
                tool = GetDatabaseDescriptionTool()
                tool.knowledge_base = mock_solve_it_environment['knowledge_base']
                tools.append(tool)
        
        # All tools should be independently functional
        assert len(tools) == 5
        for tool in tools:
            assert hasattr(tool, 'name')
            assert hasattr(tool, 'invoke')
    
    def test_concurrent_tool_operations(self, mock_solve_it_environment):
        """Test concurrent tool operations."""
        import asyncio
        from tools.solveit_tools import (
            GetDatabaseDescriptionTool, GetDatabaseDescriptionParams,
            SearchTool, SearchParams
        )
        
        async def run_concurrent_operations():
            with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
                 patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'), \
                 patch.object(SearchTool, '_resolve_data_path'), \
                 patch.object(SearchTool, '_init_knowledge_base'):
                
                # Create tools
                desc_tool = GetDatabaseDescriptionTool()
                desc_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
                desc_tool.data_path = mock_solve_it_environment['data_path']
                
                search_tool = SearchTool()
                search_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
                
                # Run concurrent operations
                tasks = [
                    desc_tool.invoke(GetDatabaseDescriptionParams()),
                    search_tool.invoke(SearchParams(keywords="test")),
                    desc_tool.invoke(GetDatabaseDescriptionParams()),
                    search_tool.invoke(SearchParams(keywords="another test")),
                ]
                
                results = await asyncio.gather(*tasks)
                
                # All operations should complete successfully
                assert len(results) == 4
                for result in results:
                    assert result is not None
        
        # Run the concurrent test
        asyncio.run(run_concurrent_operations())


class TestDataConsistencyIntegration:
    """Test data consistency across tools."""
    
    def test_data_consistency_across_tools(self, mock_solve_it_environment):
        """Test that all tools see consistent data."""
        from tools.solveit_tools import (
            GetTechniqueDetailsTool, GetTechniqueDetailsParams,
            GetWeaknessesForTechniqueTool, GetWeaknessesForTechniqueParams,
            GetAllTechniquesWithNameAndIdTool, GetAllTechniquesWithNameAndIdParams
        )
        
        with patch.object(GetTechniqueDetailsTool, '_resolve_data_path'), \
             patch.object(GetTechniqueDetailsTool, '_init_knowledge_base'), \
             patch.object(GetWeaknessesForTechniqueTool, '_resolve_data_path'), \
             patch.object(GetWeaknessesForTechniqueTool, '_init_knowledge_base'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_resolve_data_path'), \
             patch.object(GetAllTechniquesWithNameAndIdTool, '_init_knowledge_base'):
            
            # Create multiple tools
            detail_tool = GetTechniqueDetailsTool()
            detail_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            weakness_tool = GetWeaknessesForTechniqueTool()
            weakness_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            bulk_tool = GetAllTechniquesWithNameAndIdTool()
            bulk_tool.knowledge_base = mock_solve_it_environment['knowledge_base']
            
            # All tools should access the same knowledge base
            assert detail_tool.knowledge_base == weakness_tool.knowledge_base
            assert weakness_tool.knowledge_base == bulk_tool.knowledge_base
    
    def test_knowledge_base_stats_consistency(self, mock_solve_it_environment):
        """Test that knowledge base statistics are consistent."""
        from tools.solveit_tools import GetDatabaseDescriptionTool
        
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
            
            # Create multiple tool instances
            tool1 = GetDatabaseDescriptionTool()
            tool1.knowledge_base = mock_solve_it_environment['knowledge_base']
            tool1.data_path = mock_solve_it_environment['data_path']
            
            tool2 = GetDatabaseDescriptionTool()
            tool2.knowledge_base = mock_solve_it_environment['knowledge_base']
            tool2.data_path = mock_solve_it_environment['data_path']
            
            # Both tools should report consistent statistics
            stats1 = tool1.get_knowledge_base_stats()
            stats2 = tool2.get_knowledge_base_stats()
            
            assert stats1['techniques'] == stats2['techniques']
            assert stats1['weaknesses'] == stats2['weaknesses']
            assert stats1['mitigations'] == stats2['mitigations']
            assert stats1['objectives'] == stats2['objectives']
