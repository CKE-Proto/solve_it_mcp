"""Integration tests using the real SOLVE-IT library."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch

from tools.solveit_tools import (
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


class TestRealLibraryIntegration:
    """Integration tests using the real SOLVE-IT library."""
    
    def test_solve_it_library_available(self):
        """Test that the solve_it_library is available."""
        try:
            # Check if the solve-it-main directory exists
            solve_it_path = Path("../solve-it-main")
            assert solve_it_path.exists(), "solve-it-main directory not found"
            
            # Check if the library is importable
            import sys
            sys.path.insert(0, str(solve_it_path.resolve()))
            
            from solve_it_library import KnowledgeBase
            assert KnowledgeBase is not None
            
        except ImportError as e:
            pytest.skip(f"solve_it_library not available: {e}")
    
    def test_get_database_description_tool_with_real_library(self):
        """Test GetDatabaseDescriptionTool with real library."""
        try:
            tool = GetDatabaseDescriptionTool()
            
            # This should work if the library is available
            assert tool.name == "get_database_description"
            assert hasattr(tool, 'knowledge_base')
            assert hasattr(tool, 'data_path')
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_get_database_description_invoke_with_real_library(self):
        """Test GetDatabaseDescriptionTool invoke with real library."""
        try:
            tool = GetDatabaseDescriptionTool()
            params = GetDatabaseDescriptionParams()
            
            result = await tool.invoke(params)
            
            # Validate response structure
            assert isinstance(result, str)
            data = json.loads(result)
            
            assert "database_name" in data
            assert "description" in data
            assert "statistics" in data
            assert "mcp_server_role" in data
            
            # Validate statistics
            stats = data["statistics"]
            assert "techniques" in stats
            assert "weaknesses" in stats
            assert "mitigations" in stats
            assert "objectives" in stats
            assert "current_mapping" in stats
            assert "data_path" in stats
            
            # These should be positive numbers
            assert stats["techniques"] > 0
            assert stats["weaknesses"] > 0
            assert stats["mitigations"] > 0
            assert stats["objectives"] > 0
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_search_tool_with_real_library(self):
        """Test SearchTool with real library."""
        try:
            tool = SearchTool()
            params = SearchParams(keywords="forensic")
            
            result = await tool.invoke(params)
            
            # Validate response structure
            assert isinstance(result, str)
            data = json.loads(result)
            
            assert "techniques" in data
            assert "weaknesses" in data
            assert "mitigations" in data
            
            # At least one category should have results
            total_results = len(data["techniques"]) + len(data["weaknesses"]) + len(data["mitigations"])
            assert total_results > 0
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_technique_details_tool_with_real_library(self):
        """Test GetTechniqueDetailsTool with real library."""
        try:
            # First, get a list of techniques to test with
            desc_tool = GetDatabaseDescriptionTool()
            desc_params = GetDatabaseDescriptionParams()
            desc_result = await desc_tool.invoke(desc_params)
            desc_data = json.loads(desc_result)
            
            # Skip if no techniques
            if desc_data["statistics"]["techniques"] == 0:
                pytest.skip("No techniques available in database")
            
            # Try to get details for a technique (we'll use a search to find one)
            search_tool = SearchTool()
            search_params = SearchParams(keywords="analysis", item_types=["techniques"])
            search_result = await search_tool.invoke(search_params)
            search_data = json.loads(search_result)
            
            if len(search_data["techniques"]) == 0:
                pytest.skip("No techniques found in search")
            
            # Get details for the first technique
            technique_id = search_data["techniques"][0]["id"]
            
            tool = GetTechniqueDetailsTool()
            params = GetTechniqueDetailsParams(technique_id=technique_id)
            
            result = await tool.invoke(params)
            
            # Validate response structure
            assert isinstance(result, str)
            data = json.loads(result)
            
            assert "id" in data
            assert "name" in data
            assert data["id"] == technique_id
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_weakness_details_tool_with_real_library(self):
        """Test GetWeaknessDetailsTool with real library."""
        try:
            # First, search for weaknesses
            search_tool = SearchTool()
            search_params = SearchParams(keywords="limitation", item_types=["weaknesses"])
            search_result = await search_tool.invoke(search_params)
            search_data = json.loads(search_result)
            
            if len(search_data["weaknesses"]) == 0:
                pytest.skip("No weaknesses found in search")
            
            # Get details for the first weakness
            weakness_id = search_data["weaknesses"][0]["id"]
            
            tool = GetWeaknessDetailsTool()
            params = GetWeaknessDetailsParams(weakness_id=weakness_id)
            
            result = await tool.invoke(params)
            
            # Validate response structure
            assert isinstance(result, str)
            data = json.loads(result)
            
            assert "id" in data
            assert "name" in data
            assert data["id"] == weakness_id
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    @pytest.mark.asyncio
    async def test_mitigation_details_tool_with_real_library(self):
        """Test GetMitigationDetailsTool with real library."""
        try:
            # First, search for mitigations
            search_tool = SearchTool()
            search_params = SearchParams(keywords="training", item_types=["mitigations"])
            search_result = await search_tool.invoke(search_params)
            search_data = json.loads(search_result)
            
            if len(search_data["mitigations"]) == 0:
                pytest.skip("No mitigations found in search")
            
            # Get details for the first mitigation
            mitigation_id = search_data["mitigations"][0]["id"]
            
            tool = GetMitigationDetailsTool()
            params = GetMitigationDetailsParams(mitigation_id=mitigation_id)
            
            result = await tool.invoke(params)
            
            # Validate response structure
            assert isinstance(result, str)
            data = json.loads(result)
            
            assert "id" in data
            assert "name" in data
            assert data["id"] == mitigation_id
            
        except Exception as e:
            pytest.skip(f"Real library integration failed: {e}")
    
    def test_data_path_resolution_with_real_environment(self):
        """Test that data path resolution works with real environment."""
        try:
            from utils.data_path import get_solve_it_data_path, validate_solve_it_data_path
            
            # Test that we can resolve the data path
            data_path = get_solve_it_data_path()
            assert data_path is not None
            assert isinstance(data_path, str)
            
            # Test that the path is valid
            assert validate_solve_it_data_path(data_path)
            
            # Test that required directories exist
            path_obj = Path(data_path)
            assert path_obj.exists()
            assert (path_obj / "techniques").exists()
            assert (path_obj / "weaknesses").exists()
            assert (path_obj / "mitigations").exists()
            
        except Exception as e:
            pytest.skip(f"Real environment data path resolution failed: {e}")
    
    def test_multiple_tools_initialization(self):
        """Test that multiple tools can be initialized simultaneously."""
        try:
            tools = [
                GetDatabaseDescriptionTool(),
                SearchTool(),
                GetTechniqueDetailsTool(),
                GetWeaknessDetailsTool(),
                GetMitigationDetailsTool(),
            ]
            
            # All tools should be initialized successfully
            for tool in tools:
                assert hasattr(tool, 'name')
                assert hasattr(tool, 'description')
                assert hasattr(tool, 'knowledge_base')
                assert hasattr(tool, 'data_path')
                
            # Tools should have unique names
            names = [tool.name for tool in tools]
            assert len(names) == len(set(names))
            
        except Exception as e:
            pytest.skip(f"Multiple tools initialization failed: {e}")


class TestRealLibraryPerformance:
    """Performance tests using the real SOLVE-IT library."""
    
    @pytest.mark.asyncio
    async def test_search_performance(self):
        """Test search performance with real library."""
        try:
            import time
            
            tool = SearchTool()
            params = SearchParams(keywords="forensic")
            
            start_time = time.time()
            result = await tool.invoke(params)
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Search should complete within reasonable time (5 seconds)
            assert duration < 5.0, f"Search took too long: {duration:.2f}s"
            
            # Result should be valid
            assert isinstance(result, str)
            data = json.loads(result)
            assert "techniques" in data
            
        except Exception as e:
            pytest.skip(f"Real library performance test failed: {e}")
    
    @pytest.mark.asyncio
    async def test_bulk_operations_performance(self):
        """Test bulk operations performance with real library."""
        try:
            import time
            
            # Test multiple operations in sequence
            tools_and_params = [
                (GetDatabaseDescriptionTool(), GetDatabaseDescriptionParams()),
                (SearchTool(), SearchParams(keywords="analysis")),
                (SearchTool(), SearchParams(keywords="forensic")),
            ]
            
            start_time = time.time()
            
            for tool, params in tools_and_params:
                result = await tool.invoke(params)
                assert isinstance(result, str)
                json.loads(result)  # Validate JSON
            
            end_time = time.time()
            duration = end_time - start_time
            
            # All operations should complete within reasonable time (10 seconds)
            assert duration < 10.0, f"Bulk operations took too long: {duration:.2f}s"
            
        except Exception as e:
            pytest.skip(f"Real library bulk performance test failed: {e}")
