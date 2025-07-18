"""SOLVE-IT MCP Tools - Core tools for accessing the SOLVE-IT knowledge base."""

import json
from typing import Any, Dict, List, Optional

from pydantic import Field

from .solveit_base import SolveItBaseTool, ToolParams


class GetDatabaseDescriptionParams(ToolParams):
    """Parameters for get_database_description tool."""
    # No parameters needed for this tool
    pass


class GetDatabaseDescriptionTool(SolveItBaseTool[GetDatabaseDescriptionParams]):
    """Tool to get a comprehensive description of the SOLVE-IT database."""
    
    name = "get_database_description"
    description = "Returns a comprehensive description of the SOLVE-IT database and the role of this MCP server."
    Params = GetDatabaseDescriptionParams
    
    async def invoke(self, params: GetDatabaseDescriptionParams) -> str:
        """Get database description and server information."""
        try:
            stats = self.get_knowledge_base_stats()
            
            description = {
                "database_name": "SOLVE-IT Digital Forensics Knowledge Base",
                "description": "A systematic digital forensics knowledge base inspired by MITRE ATT&CK",
                "purpose": "Provides comprehensive mapping of digital forensic investigation techniques, weaknesses, and mitigations",
                "components": {
                    "techniques": "Digital forensic investigation methods (T1001, T1002, etc.)",
                    "weaknesses": "Potential problems/limitations of techniques (W1001, W1002, etc.)",
                    "mitigations": "Ways to address weaknesses (M1001, M1002, etc.)",
                    "objectives": "Categories that organize techniques by investigation goals"
                },
                "statistics": stats,
                "mcp_server_role": "This MCP server provides LLMs with programmatic access to the SOLVE-IT knowledge base through type-safe, validated tools",
                "available_operations": [
                    "Search across techniques, weaknesses, and mitigations",
                    "Retrieve detailed information by ID",
                    "Explore relationships between components",
                    "Work with different objective mappings",
                    "Bulk retrieval operations"
                ]
            }
            
            return json.dumps(description, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "database description retrieval")


class SearchParams(ToolParams):
    """Parameters for search tool."""
    keywords: str = Field(description="Keywords to search for. Use quotes for exact phrases.")
    item_types: Optional[List[str]] = Field(
        default=None,
        description="Types of items to search ('techniques', 'weaknesses', 'mitigations'). If None, searches all types."
    )


class SearchTool(SolveItBaseTool[SearchParams]):
    """Tool to search the knowledge base for techniques, weaknesses, or mitigations."""
    
    name = "search"
    description = "Searches the knowledge base for techniques, weaknesses, or mitigations matching specified keywords."
    Params = SearchParams
    
    async def invoke(self, params: SearchParams) -> str:
        """Search the knowledge base."""
        try:
            results = self.knowledge_base.search(
                keywords=params.keywords,
                item_types=params.item_types
            )
            
            return json.dumps(results, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "search operation")


class GetTechniqueDetailsParams(ToolParams):
    """Parameters for get_technique_details tool."""
    technique_id: str = Field(description="The ID of the technique (e.g., T1002)")


class GetTechniqueDetailsTool(SolveItBaseTool[GetTechniqueDetailsParams]):
    """Tool to retrieve full details for a specific SOLVE-IT technique."""
    
    name = "get_technique_details"
    description = "Retrieves the full details for a specific SOLVE-IT technique by its ID (e.g., T1002)."
    Params = GetTechniqueDetailsParams
    
    async def invoke(self, params: GetTechniqueDetailsParams) -> str:
        """Get technique details."""
        try:
            technique = self.knowledge_base.get_technique(params.technique_id)
            
            if technique is None:
                return f"Technique {params.technique_id} not found."
            
            return json.dumps(technique, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"technique {params.technique_id} retrieval")


class GetWeaknessDetailsParams(ToolParams):
    """Parameters for get_weakness_details tool."""
    weakness_id: str = Field(description="The ID of the weakness (e.g., W1001)")


class GetWeaknessDetailsTool(SolveItBaseTool[GetWeaknessDetailsParams]):
    """Tool to retrieve additional details for a specific SOLVE-IT weakness."""
    
    name = "get_weakness_details"
    description = "Retrieves additional, optional details for a specific SOLVE-IT weakness by its ID (e.g., W1001). The 'name' field contains the primary description of what this weakness entails."
    Params = GetWeaknessDetailsParams
    
    async def invoke(self, params: GetWeaknessDetailsParams) -> str:
        """Get weakness details."""
        try:
            weakness = self.knowledge_base.get_weakness(params.weakness_id)
            
            if weakness is None:
                return f"Weakness {params.weakness_id} not found."
            
            return json.dumps(weakness, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"weakness {params.weakness_id} retrieval")


class GetMitigationDetailsParams(ToolParams):
    """Parameters for get_mitigation_details tool."""
    mitigation_id: str = Field(description="The ID of the mitigation (e.g., M1001)")


class GetMitigationDetailsTool(SolveItBaseTool[GetMitigationDetailsParams]):
    """Tool to retrieve additional details for a specific SOLVE-IT mitigation."""
    
    name = "get_mitigation_details"
    description = "Retrieves additional, optional details for a specific SOLVE-IT mitigation by its ID (e.g., M1001). The 'name' field contains the primary description of what this mitigation entails."
    Params = GetMitigationDetailsParams
    
    async def invoke(self, params: GetMitigationDetailsParams) -> str:
        """Get mitigation details."""
        try:
            mitigation = self.knowledge_base.get_mitigation(params.mitigation_id)
            
            if mitigation is None:
                return f"Mitigation {params.mitigation_id} not found."
            
            return json.dumps(mitigation, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"mitigation {params.mitigation_id} retrieval")


class GetWeaknessesForTechniqueParams(ToolParams):
    """Parameters for get_weaknesses_for_technique tool."""
    technique_id: str = Field(description="The ID of the technique")


class GetWeaknessesForTechniqueTool(SolveItBaseTool[GetWeaknessesForTechniqueParams]):
    """Tool to retrieve all weaknesses associated with a specific technique."""
    
    name = "get_weaknesses_for_technique"
    description = "Retrieves all weaknesses associated with a specific SOLVE-IT technique ID."
    Params = GetWeaknessesForTechniqueParams
    
    async def invoke(self, params: GetWeaknessesForTechniqueParams) -> str:
        """Get weaknesses for a technique."""
        try:
            weaknesses = self.knowledge_base.get_weaknesses_for_technique(params.technique_id)
            
            return json.dumps(weaknesses, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"weaknesses for technique {params.technique_id}")


class GetMitigationsForWeaknessParams(ToolParams):
    """Parameters for get_mitigations_for_weakness tool."""
    weakness_id: str = Field(description="The ID of the weakness")


class GetMitigationsForWeaknessTool(SolveItBaseTool[GetMitigationsForWeaknessParams]):
    """Tool to retrieve all mitigations associated with a specific weakness."""
    
    name = "get_mitigations_for_weakness"
    description = "Retrieves all mitigations associated with a specific SOLVE-IT weakness ID."
    Params = GetMitigationsForWeaknessParams
    
    async def invoke(self, params: GetMitigationsForWeaknessParams) -> str:
        """Get mitigations for a weakness."""
        try:
            mitigations = self.knowledge_base.get_mitigations_for_weakness(params.weakness_id)
            
            return json.dumps(mitigations, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"mitigations for weakness {params.weakness_id}")


# =============================================================================
# Reverse Relationships
# =============================================================================

class GetTechniquesForWeaknessParams(ToolParams):
    """Parameters for get_techniques_for_weakness tool."""
    weakness_id: str = Field(description="The ID of the weakness")


class GetTechniquesForWeaknessTool(SolveItBaseTool[GetTechniquesForWeaknessParams]):
    """Tool to retrieve all techniques that reference a specific weakness."""
    
    name = "get_techniques_for_weakness"
    description = "Retrieves all techniques that reference a specific SOLVE-IT weakness ID."
    Params = GetTechniquesForWeaknessParams
    
    async def invoke(self, params: GetTechniquesForWeaknessParams) -> str:
        """Get techniques that reference a weakness."""
        try:
            techniques = self.knowledge_base.get_techniques_for_weakness(params.weakness_id)
            
            return json.dumps(techniques, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"techniques for weakness {params.weakness_id}")


class GetWeaknessesForMitigationParams(ToolParams):
    """Parameters for get_weaknesses_for_mitigation tool."""
    mitigation_id: str = Field(description="The ID of the mitigation")


class GetWeaknessesForMitigationTool(SolveItBaseTool[GetWeaknessesForMitigationParams]):
    """Tool to retrieve all weaknesses that reference a specific mitigation."""
    
    name = "get_weaknesses_for_mitigation"
    description = "Retrieves all weaknesses that reference a specific SOLVE-IT mitigation ID."
    Params = GetWeaknessesForMitigationParams
    
    async def invoke(self, params: GetWeaknessesForMitigationParams) -> str:
        """Get weaknesses that reference a mitigation."""
        try:
            weaknesses = self.knowledge_base.get_weaknesses_for_mitigation(params.mitigation_id)
            
            return json.dumps(weaknesses, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"weaknesses for mitigation {params.mitigation_id}")


class GetTechniquesForMitigationParams(ToolParams):
    """Parameters for get_techniques_for_mitigation tool."""
    mitigation_id: str = Field(description="The ID of the mitigation")


class GetTechniquesForMitigationTool(SolveItBaseTool[GetTechniquesForMitigationParams]):
    """Tool to retrieve all techniques that reference a specific mitigation (through weaknesses)."""
    
    name = "get_techniques_for_mitigation"
    description = "Retrieves all techniques that reference a specific SOLVE-IT mitigation ID (through weaknesses)."
    Params = GetTechniquesForMitigationParams
    
    async def invoke(self, params: GetTechniquesForMitigationParams) -> str:
        """Get techniques that reference a mitigation."""
        try:
            techniques = self.knowledge_base.get_techniques_for_mitigation(params.mitigation_id)
            
            return json.dumps(techniques, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"techniques for mitigation {params.mitigation_id}")


# =============================================================================
# HIGH PRIORITY TOOLS - Objective/Mapping Management
# =============================================================================

class ListObjectivesParams(ToolParams):
    """Parameters for list_objectives tool."""
    # No parameters needed for this tool
    pass


class ListObjectivesTool(SolveItBaseTool[ListObjectivesParams]):
    """Tool to list all objectives from the current mapping."""
    
    name = "list_objectives"
    description = "Lists all objectives from the current SOLVE-IT objective mapping."
    Params = ListObjectivesParams
    
    async def invoke(self, params: ListObjectivesParams) -> str:
        """List all objectives."""
        try:
            objectives = self.knowledge_base.list_objectives()
            
            return json.dumps(objectives, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "objectives listing")


class GetTechniquesForObjectiveParams(ToolParams):
    """Parameters for get_techniques_for_objective tool."""
    objective_name: str = Field(description="The name of the objective")


class GetTechniquesForObjectiveTool(SolveItBaseTool[GetTechniquesForObjectiveParams]):
    """Tool to retrieve all techniques for a specific objective."""
    
    name = "get_techniques_for_objective"
    description = "Retrieves all techniques associated with a specific SOLVE-IT objective name."
    Params = GetTechniquesForObjectiveParams
    
    async def invoke(self, params: GetTechniquesForObjectiveParams) -> str:
        """Get techniques for an objective."""
        try:
            techniques = self.knowledge_base.get_techniques_for_objective(params.objective_name)
            
            return json.dumps(techniques, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"techniques for objective {params.objective_name}")


class ListAvailableMappingsParams(ToolParams):
    """Parameters for list_available_mappings tool."""
    # No parameters needed for this tool
    pass


class ListAvailableMappingsTool(SolveItBaseTool[ListAvailableMappingsParams]):
    """Tool to list all available objective mapping files."""
    
    name = "list_available_mappings"
    description = "Lists all available SOLVE-IT objective mapping files (solve-it.json, carrier.json, etc.)."
    Params = ListAvailableMappingsParams
    
    async def invoke(self, params: ListAvailableMappingsParams) -> str:
        """List available mapping files."""
        try:
            mappings = self.knowledge_base.list_available_mappings()
            
            return json.dumps(mappings, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "available mappings listing")


class LoadObjectiveMappingParams(ToolParams):
    """Parameters for load_objective_mapping tool."""
    filename: str = Field(description="The filename of the mapping to load (e.g., 'carrier.json')")


class LoadObjectiveMappingTool(SolveItBaseTool[LoadObjectiveMappingParams]):
    """Tool to switch to a different objective mapping."""
    
    name = "load_objective_mapping"
    description = "Switches to a different SOLVE-IT objective mapping file."
    Params = LoadObjectiveMappingParams
    
    async def invoke(self, params: LoadObjectiveMappingParams) -> str:
        """Load a different objective mapping."""
        try:
            success = self.knowledge_base.load_objective_mapping(params.filename)
            
            if success:
                result = {
                    "success": True,
                    "message": f"Successfully loaded mapping: {params.filename}",
                    "current_mapping": params.filename
                }
            else:
                result = {
                    "success": False,
                    "message": f"Failed to load mapping: {params.filename}",
                    "current_mapping": self.knowledge_base.current_mapping_name
                }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, f"loading mapping {params.filename}")


# =============================================================================
# MEDIUM PRIORITY TOOLS - Bulk Retrieval (Concise Format)
# =============================================================================

class GetAllTechniquesWithNameAndIdParams(ToolParams):
    """Parameters for get_all_techniques_with_name_and_id tool."""
    # No parameters needed for this tool
    pass


class GetAllTechniquesWithNameAndIdTool(SolveItBaseTool[GetAllTechniquesWithNameAndIdParams]):
    """Tool to retrieve all techniques with ID and name only."""
    
    name = "get_all_techniques_with_name_and_id"
    description = "Retrieves all SOLVE-IT techniques with ID and name only (concise format)."
    Params = GetAllTechniquesWithNameAndIdParams
    
    async def invoke(self, params: GetAllTechniquesWithNameAndIdParams) -> str:
        """Get all techniques with ID and name only."""
        try:
            techniques = self.knowledge_base.get_all_techniques_with_name_and_id()
            
            return json.dumps(techniques, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all techniques with name and ID")


class GetAllWeaknessesWithNameAndIdParams(ToolParams):
    """Parameters for get_all_weaknesses_with_name_and_id tool."""
    # No parameters needed for this tool
    pass


class GetAllWeaknessesWithNameAndIdTool(SolveItBaseTool[GetAllWeaknessesWithNameAndIdParams]):
    """Tool to retrieve all weaknesses with ID and name only."""
    
    name = "get_all_weaknesses_with_name_and_id"
    description = "Retrieves all SOLVE-IT weaknesses with ID and name only (concise format)."
    Params = GetAllWeaknessesWithNameAndIdParams
    
    async def invoke(self, params: GetAllWeaknessesWithNameAndIdParams) -> str:
        """Get all weaknesses with ID and name only."""
        try:
            weaknesses = self.knowledge_base.get_all_weaknesses_with_name_and_id()
            
            return json.dumps(weaknesses, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all weaknesses with name and ID")


class GetAllMitigationsWithNameAndIdParams(ToolParams):
    """Parameters for get_all_mitigations_with_name_and_id tool."""
    # No parameters needed for this tool
    pass


class GetAllMitigationsWithNameAndIdTool(SolveItBaseTool[GetAllMitigationsWithNameAndIdParams]):
    """Tool to retrieve all mitigations with ID and name only."""
    
    name = "get_all_mitigations_with_name_and_id"
    description = "Retrieves all SOLVE-IT mitigations with ID and name only (concise format)."
    Params = GetAllMitigationsWithNameAndIdParams
    
    async def invoke(self, params: GetAllMitigationsWithNameAndIdParams) -> str:
        """Get all mitigations with ID and name only."""
        try:
            mitigations = self.knowledge_base.get_all_mitigations_with_name_and_id()
            
            return json.dumps(mitigations, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all mitigations with name and ID")


# =============================================================================
# MEDIUM PRIORITY TOOLS - Bulk Retrieval (Full Detail Format)
# =============================================================================

class GetAllTechniquesWithFullDetailParams(ToolParams):
    """Parameters for get_all_techniques_with_full_detail tool."""
    # No parameters needed for this tool
    pass


class GetAllTechniquesWithFullDetailTool(SolveItBaseTool[GetAllTechniquesWithFullDetailParams]):
    """Tool to retrieve all techniques with complete details."""
    
    name = "get_all_techniques_with_full_detail"
    description = "Retrieves all SOLVE-IT techniques with complete details. Warning: May return large amounts of data."
    Params = GetAllTechniquesWithFullDetailParams
    
    async def invoke(self, params: GetAllTechniquesWithFullDetailParams) -> str:
        """Get all techniques with full details."""
        try:
            techniques = self.knowledge_base.get_all_techniques_with_full_detail()
            
            return json.dumps(techniques, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all techniques with full detail")


class GetAllWeaknessesWithFullDetailParams(ToolParams):
    """Parameters for get_all_weaknesses_with_full_detail tool."""
    # No parameters needed for this tool
    pass


class GetAllWeaknessesWithFullDetailTool(SolveItBaseTool[GetAllWeaknessesWithFullDetailParams]):
    """Tool to retrieve all weaknesses with complete details."""
    
    name = "get_all_weaknesses_with_full_detail"
    description = "Retrieves all SOLVE-IT weaknesses with complete details. Warning: May return large amounts of data."
    Params = GetAllWeaknessesWithFullDetailParams
    
    async def invoke(self, params: GetAllWeaknessesWithFullDetailParams) -> str:
        """Get all weaknesses with full details."""
        try:
            weaknesses = self.knowledge_base.get_all_weaknesses_with_full_detail()
            
            return json.dumps(weaknesses, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all weaknesses with full detail")


class GetAllMitigationsWithFullDetailParams(ToolParams):
    """Parameters for get_all_mitigations_with_full_detail tool."""
    # No parameters needed for this tool
    pass


class GetAllMitigationsWithFullDetailTool(SolveItBaseTool[GetAllMitigationsWithFullDetailParams]):
    """Tool to retrieve all mitigations with complete details."""
    
    name = "get_all_mitigations_with_full_detail"
    description = "Retrieves all SOLVE-IT mitigations with complete details. Warning: May return large amounts of data."
    Params = GetAllMitigationsWithFullDetailParams
    
    async def invoke(self, params: GetAllMitigationsWithFullDetailParams) -> str:
        """Get all mitigations with full details."""
        try:
            mitigations = self.knowledge_base.get_all_mitigations_with_full_detail()
            
            return json.dumps(mitigations, indent=2)
            
        except Exception as e:
            return self.handle_knowledge_base_error(e, "all mitigations with full detail")
