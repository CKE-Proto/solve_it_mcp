"""Unit tests for parameter validation across all tools."""

import pytest
from pydantic import ValidationError

from solveit_mcp_server.tools.solveit_tools import (
    # Essential query tools
    GetDatabaseDescriptionParams,
    SearchParams,
    GetTechniqueDetailsParams,
    GetWeaknessDetailsParams,
    GetMitigationDetailsParams,
    # Relationship tools
    GetWeaknessesForTechniqueParams,
    GetMitigationsForWeaknessParams,
    GetTechniquesForWeaknessParams,
    GetWeaknessesForMitigationParams,
    GetTechniquesForMitigationParams,
    # Objective tools
    ListObjectivesParams,
    GetTechniquesForObjectiveParams,
    ListAvailableMappingsParams,
    LoadObjectiveMappingParams,
    # Bulk tools
    GetAllTechniquesWithNameAndIdParams,
    GetAllWeaknessesWithNameAndIdParams,
    GetAllMitigationsWithNameAndIdParams,
    GetAllTechniquesWithFullDetailParams,
    GetAllWeaknessesWithFullDetailParams,
    GetAllMitigationsWithFullDetailParams,
)


class TestParameterValidation:
    """Test parameter validation for all tool parameter classes."""
    
    def test_no_params_classes(self):
        """Test parameter classes that require no parameters."""
        # These should all be created without parameters
        no_param_classes = [
            GetDatabaseDescriptionParams,
            ListObjectivesParams,
            ListAvailableMappingsParams,
            GetAllTechniquesWithNameAndIdParams,
            GetAllWeaknessesWithNameAndIdParams,
            GetAllMitigationsWithNameAndIdParams,
            GetAllTechniquesWithFullDetailParams,
            GetAllWeaknessesWithFullDetailParams,
            GetAllMitigationsWithFullDetailParams,
        ]
        
        for param_class in no_param_classes:
            # Should create successfully without parameters
            params = param_class()
            assert params is not None
            
            # Should also work with empty dict
            params = param_class(**{})
            assert params is not None
    
    def test_search_params_validation(self):
        """Test SearchParams validation."""
        # Valid parameters
        params = SearchParams(keywords="test search")
        assert params.keywords == "test search"
        assert params.item_types is None
        
        # Valid with item_types
        params = SearchParams(keywords="test", item_types=["techniques", "weaknesses"])
        assert params.keywords == "test"
        assert params.item_types == ["techniques", "weaknesses"]
        
        # Valid with empty item_types
        params = SearchParams(keywords="test", item_types=[])
        assert params.keywords == "test"
        assert params.item_types == []
        
        # Invalid - missing keywords
        with pytest.raises(ValidationError):
            SearchParams()
        
        # Invalid - empty keywords
        with pytest.raises(ValidationError):
            SearchParams(keywords="")
    
    def test_id_based_params_validation(self):
        """Test parameter classes that require ID parameters."""
        # Test technique ID parameters
        params = GetTechniqueDetailsParams(technique_id="T1001")
        assert params.technique_id == "T1001"
        
        params = GetWeaknessesForTechniqueParams(technique_id="T1002")
        assert params.technique_id == "T1002"
        
        # Test weakness ID parameters
        params = GetWeaknessDetailsParams(weakness_id="W1001")
        assert params.weakness_id == "W1001"
        
        params = GetMitigationsForWeaknessParams(weakness_id="W1002")
        assert params.weakness_id == "W1002"
        
        params = GetTechniquesForWeaknessParams(weakness_id="W1003")
        assert params.weakness_id == "W1003"
        
        # Test mitigation ID parameters
        params = GetMitigationDetailsParams(mitigation_id="M1001")
        assert params.mitigation_id == "M1001"
        
        params = GetWeaknessesForMitigationParams(mitigation_id="M1002")
        assert params.mitigation_id == "M1002"
        
        params = GetTechniquesForMitigationParams(mitigation_id="M1003")
        assert params.mitigation_id == "M1003"
        
        # Test invalid cases - missing required parameters
        with pytest.raises(ValidationError):
            GetTechniqueDetailsParams()
        
        with pytest.raises(ValidationError):
            GetWeaknessDetailsParams()
        
        with pytest.raises(ValidationError):
            GetMitigationDetailsParams()
    
    def test_objective_params_validation(self):
        """Test objective-related parameter validation."""
        # Valid objective name
        params = GetTechniquesForObjectiveParams(objective_name="Test Objective")
        assert params.objective_name == "Test Objective"
        
        # Valid with spaces and special characters
        params = GetTechniquesForObjectiveParams(objective_name="Test Objective - Part 1")
        assert params.objective_name == "Test Objective - Part 1"
        
        # Invalid - missing objective_name
        with pytest.raises(ValidationError):
            GetTechniquesForObjectiveParams()
        
        # Invalid - empty objective_name
        with pytest.raises(ValidationError):
            GetTechniquesForObjectiveParams(objective_name="")
    
    def test_mapping_params_validation(self):
        """Test mapping-related parameter validation."""
        # Valid filename
        params = LoadObjectiveMappingParams(filename="carrier.json")
        assert params.filename == "carrier.json"
        
        # Valid with different extensions
        params = LoadObjectiveMappingParams(filename="test.json")
        assert params.filename == "test.json"
        
        # Valid with path-like filename
        params = LoadObjectiveMappingParams(filename="subdir/test.json")
        assert params.filename == "subdir/test.json"
        
        # Invalid - missing filename
        with pytest.raises(ValidationError):
            LoadObjectiveMappingParams()
        
        # Invalid - empty filename
        with pytest.raises(ValidationError):
            LoadObjectiveMappingParams(filename="")
    
    def test_parameter_type_validation(self):
        """Test that parameters validate types correctly."""
        # Test string type validation
        with pytest.raises(ValidationError):
            GetTechniqueDetailsParams(technique_id=123)  # Should be string
        
        with pytest.raises(ValidationError):
            GetTechniquesForObjectiveParams(objective_name=None)  # Should be string
        
        # Test list type validation for SearchParams
        with pytest.raises(ValidationError):
            SearchParams(keywords="test", item_types="techniques")  # Should be list
        
        # Valid list
        params = SearchParams(keywords="test", item_types=["techniques"])
        assert params.item_types == ["techniques"]
    
    def test_parameter_field_descriptions(self):
        """Test that parameter classes have proper field descriptions."""
        # Check that required fields have descriptions
        params = GetTechniqueDetailsParams(technique_id="T1001")
        schema = params.model_json_schema()
        
        assert 'technique_id' in schema['properties']
        assert 'description' in schema['properties']['technique_id']
        assert 'T1002' in schema['properties']['technique_id']['description']
        
        # Check SearchParams has descriptions
        params = SearchParams(keywords="test")
        schema = params.model_json_schema()
        
        assert 'keywords' in schema['properties']
        assert 'description' in schema['properties']['keywords']
        assert 'item_types' in schema['properties']
        assert 'description' in schema['properties']['item_types']
    
    def test_parameter_serialization(self):
        """Test that parameters can be serialized and deserialized correctly."""
        # Test SearchParams
        original = SearchParams(keywords="test search", item_types=["techniques", "weaknesses"])
        json_data = original.model_dump()
        recreated = SearchParams(**json_data)
        
        assert recreated.keywords == original.keywords
        assert recreated.item_types == original.item_types
        
        # Test GetTechniqueDetailsParams
        original = GetTechniqueDetailsParams(technique_id="T1001")
        json_data = original.model_dump()
        recreated = GetTechniqueDetailsParams(**json_data)
        
        assert recreated.technique_id == original.technique_id
        
        # Test GetTechniquesForObjectiveParams
        original = GetTechniquesForObjectiveParams(objective_name="Test Objective")
        json_data = original.model_dump()
        recreated = GetTechniquesForObjectiveParams(**json_data)
        
        assert recreated.objective_name == original.objective_name
    
    def test_parameter_inheritance(self):
        """Test that all parameter classes inherit from ToolParams."""
        from solveit_mcp_server.tools.solveit_base import ToolParams
        
        all_param_classes = [
            GetDatabaseDescriptionParams,
            SearchParams,
            GetTechniqueDetailsParams,
            GetWeaknessDetailsParams,
            GetMitigationDetailsParams,
            GetWeaknessesForTechniqueParams,
            GetMitigationsForWeaknessParams,
            GetTechniquesForWeaknessParams,
            GetWeaknessesForMitigationParams,
            GetTechniquesForMitigationParams,
            ListObjectivesParams,
            GetTechniquesForObjectiveParams,
            ListAvailableMappingsParams,
            LoadObjectiveMappingParams,
            GetAllTechniquesWithNameAndIdParams,
            GetAllWeaknessesWithNameAndIdParams,
            GetAllMitigationsWithNameAndIdParams,
            GetAllTechniquesWithFullDetailParams,
            GetAllWeaknessesWithFullDetailParams,
            GetAllMitigationsWithFullDetailParams,
        ]
        
        for param_class in all_param_classes:
            assert issubclass(param_class, ToolParams), f"{param_class.__name__} should inherit from ToolParams"
    
    def test_parameter_defaults(self):
        """Test parameter default values."""
        # SearchParams should have item_types default to None
        params = SearchParams(keywords="test")
        assert params.item_types is None
        
        # No-param classes should work with defaults
        params = GetDatabaseDescriptionParams()
        assert params is not None
        
        params = ListObjectivesParams()
        assert params is not None
    
    def test_parameter_validation_edge_cases(self):
        """Test edge cases for parameter validation."""
        # Test with whitespace-only strings
        with pytest.raises(ValidationError):
            GetTechniqueDetailsParams(technique_id="   ")
        
        with pytest.raises(ValidationError):
            GetTechniquesForObjectiveParams(objective_name="   ")
        
        # Test with very long strings (should be accepted)
        long_string = "a" * 1000
        params = GetTechniqueDetailsParams(technique_id=long_string)
        assert params.technique_id == long_string
        
        # Test with special characters
        params = GetTechniquesForObjectiveParams(objective_name="Test & Objective (Part 1)")
        assert params.objective_name == "Test & Objective (Part 1)"
        
        # Test with unicode characters
        params = GetTechniquesForObjectiveParams(objective_name="Test Objectif é")
        assert params.objective_name == "Test Objectif é"
