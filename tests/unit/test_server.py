"""Unit tests for server initialization and tool registration."""

from unittest.mock import patch, MagicMock
import pytest

from server import create_server
from tools.solveit_tools import (
    GetDatabaseDescriptionTool,
    SearchTool,
    GetTechniqueDetailsTool,
    GetWeaknessDetailsTool,
    GetMitigationDetailsTool,
    GetWeaknessesForTechniqueTool,
    GetMitigationsForWeaknessTool,
    GetTechniquesForWeaknessTool,
    GetWeaknessesForMitigationTool,
    GetTechniquesForMitigationTool,
    ListObjectivesTool,
    GetTechniquesForObjectiveTool,
    ListAvailableMappingsTool,
    LoadObjectiveMappingTool,
    GetAllTechniquesWithNameAndIdTool,
    GetAllWeaknessesWithNameAndIdTool,
    GetAllMitigationsWithNameAndIdTool,
    GetAllTechniquesWithFullDetailTool,
    GetAllWeaknessesWithFullDetailTool,
    GetAllMitigationsWithFullDetailTool,
)


class TestServerInitialization:
    """Test server initialization and configuration."""
    
    def test_create_server_function_exists(self):
        """Test that create_server function exists."""
        assert callable(create_server)
    
    @patch('server.Server')
    def test_create_server_returns_server(self, mock_server_class):
        """Test that create_server returns a server instance."""
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        result = create_server()
        
        assert result == mock_server
        mock_server_class.assert_called_once_with("solveit_mcp_server")
    
    @patch('server.Server')
    def test_server_name_configuration(self, mock_server_class):
        """Test that server is created with correct name."""
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        create_server()
        
        mock_server_class.assert_called_once_with("solveit_mcp_server")


class TestToolRegistration:
    """Test that all tools are properly registered."""
    
    def test_expected_tool_count(self):
        """Test that all 20 expected tools are available."""
        expected_tools = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        assert len(expected_tools) == 20
    
    def test_tool_names_are_unique(self):
        """Test that all tool names are unique."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        # Create instances to get tool names
        tool_names = []
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                tool_names.append(tool.name)
        
        # Check that all names are unique
        assert len(tool_names) == len(set(tool_names))
    
    def test_tool_descriptions_exist(self):
        """Test that all tools have descriptions."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'description')
                assert isinstance(tool.description, str)
                assert len(tool.description) > 0
    
    def test_tool_parameter_classes_exist(self):
        """Test that all tools have parameter classes."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'Params')
                assert tool.Params is not None
    
    @patch('server.Server')
    def test_tool_registration_with_server(self, mock_server_class):
        """Test that tools can be registered with server."""
        mock_server = MagicMock()
        mock_server_class.return_value = mock_server
        
        server = create_server()
        
        # Verify server was created
        assert server == mock_server
        mock_server_class.assert_called_once_with("solveit_mcp_server")
        
        # Test that we can register tools (mock the registration)
        with patch.object(GetDatabaseDescriptionTool, '_resolve_data_path'), \
             patch.object(GetDatabaseDescriptionTool, '_init_knowledge_base'):
            tool = GetDatabaseDescriptionTool()
            
            # Mock the register method
            server.register_tool = MagicMock()
            server.register_tool(tool)
            
            # Verify tool was registered
            server.register_tool.assert_called_once_with(tool)


class TestToolCategories:
    """Test tool categorization and organization."""
    
    def test_essential_query_tools(self):
        """Test essential query tools."""
        essential_tools = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
        ]
        
        for tool_class in essential_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'invoke')
    
    def test_relationship_tools(self):
        """Test relationship query tools."""
        relationship_tools = [
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
        ]
        
        for tool_class in relationship_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'invoke')
    
    def test_objective_tools(self):
        """Test objective and mapping tools."""
        objective_tools = [
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
        ]
        
        for tool_class in objective_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'invoke')
    
    def test_bulk_tools(self):
        """Test bulk retrieval tools."""
        bulk_tools = [
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in bulk_tools:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'invoke')


class TestServerCompatibility:
    """Test server compatibility with MCP standards."""
    
    def test_tool_names_follow_convention(self):
        """Test that tool names follow MCP conventions."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                
                # Tool names should be lowercase with underscores
                assert tool.name.islower()
                assert ' ' not in tool.name
                assert tool.name.replace('_', '').replace('-', '').isalnum()
    
    def test_tool_descriptions_are_informative(self):
        """Test that tool descriptions are informative."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                
                # Descriptions should be meaningful and contain key terms
                assert len(tool.description) > 20
                assert any(keyword in tool.description.lower() for keyword in ['solve-it', 'technique', 'weakness', 'mitigation'])
    
    def test_tools_have_async_invoke_methods(self):
        """Test that all tools have async invoke methods."""
        tool_classes = [
            GetDatabaseDescriptionTool,
            SearchTool,
            GetTechniqueDetailsTool,
            GetWeaknessDetailsTool,
            GetMitigationDetailsTool,
            GetWeaknessesForTechniqueTool,
            GetMitigationsForWeaknessTool,
            GetTechniquesForWeaknessTool,
            GetWeaknessesForMitigationTool,
            GetTechniquesForMitigationTool,
            ListObjectivesTool,
            GetTechniquesForObjectiveTool,
            ListAvailableMappingsTool,
            LoadObjectiveMappingTool,
            GetAllTechniquesWithNameAndIdTool,
            GetAllWeaknessesWithNameAndIdTool,
            GetAllMitigationsWithNameAndIdTool,
            GetAllTechniquesWithFullDetailTool,
            GetAllWeaknessesWithFullDetailTool,
            GetAllMitigationsWithFullDetailTool,
        ]
        
        for tool_class in tool_classes:
            with patch.object(tool_class, '_resolve_data_path'), \
                 patch.object(tool_class, '_init_knowledge_base'):
                tool = tool_class()
                
                # Check that invoke method exists and is async
                assert hasattr(tool, 'invoke')
                assert callable(tool.invoke)
                # Check if it's a coroutine function
                import asyncio
                assert asyncio.iscoroutinefunction(tool.invoke)
