# SOLVE-IT MCP Server

**MCP server providing LLM access to the SOLVE-IT Digital Forensics Knowledge Base.**

SOLVE-IT is a systematic digital forensics knowledge base inspired by MITRE ATT&CK, containing comprehensive mappings of investigation techniques, weaknesses, and mitigations. This MCP server exposes the entire SOLVE-IT knowledge base through tools that enable LLMs to assist with discussions and use cases related to digital forensics.

## What is SOLVE-IT?

SOLVE-IT provides a structured approach to digital forensics investigations through:

- **Techniques** (T1001, T1002...): Digital forensic investigation methods
- **Weaknesses** (W1001, W1002...): Potential problems/limitations of techniques  
- **Mitigations** (M1001, M1002...): Ways to address weaknesses
- **Objectives**: Categories that organize techniques by investigation goals

See the main repository here: https://github.com/SOLVE-IT-DF/solve-it

## Quick Start

### 1. Prerequisites

Ensure you have the SOLVE-IT knowledge base available:

https://github.com/SOLVE-IT-DF/solve-it.git


### 2. Install the MCP Server

```bash
git clone <this-repository>
cd solve_it_mcp
pip install -e .
```

### 3. Run the Server

```bash
python3 src/server.py
```

### 4. Configure MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "solveit": {
      "command": "python3",
      "args": ["/path/to/solve_it_mcp/src/server.py"],
      "cwd": "/path/to/solve_it_mcp"
    }
  }
}
```

## Available Tools

The server provides 20 tools organized into functional categories:

### Core Information Tools

#### `get_database_description`
Get comprehensive overview of the SOLVE-IT database and server capabilities.

**Parameters:** None

**Example:**
```
Tool: get_database_description
Result: Complete database statistics and server information
```

#### `search`
Search across techniques, weaknesses, and mitigations using keywords.

**Parameters:**
- `keywords` (string): Search terms. Use quotes for exact phrases
- `item_types` (array, optional): Filter by type: `["techniques", "weaknesses", "mitigations"]`

**Examples:**
```
Tool: search
Parameters: {"keywords": "network analysis", "item_types": ["techniques"]}

Tool: search  
Parameters: {"keywords": "\"log analysis\""}
```

### Detailed Lookup Tools

#### `get_technique_details`
Retrieve complete information for a specific technique.

**Parameters:**
- `technique_id` (string): Technique ID (e.g., "T1002")

#### `get_weakness_details`
Retrieve detailed information for a specific weakness.

**Parameters:**
- `weakness_id` (string): Weakness ID (e.g., "W1001")

#### `get_mitigation_details`
Retrieve detailed information for a specific mitigation.

**Parameters:**
- `mitigation_id` (string): Mitigation ID (e.g., "M1001")

### Relationship Analysis Tools

#### `get_weaknesses_for_technique`
Find all weaknesses associated with a technique.

**Parameters:**
- `technique_id` (string): Technique ID

#### `get_mitigations_for_weakness`
Find all mitigations that address a specific weakness.

**Parameters:**
- `weakness_id` (string): Weakness ID

#### `get_techniques_for_weakness`
Find all techniques that have a specific weakness.

**Parameters:**
- `weakness_id` (string): Weakness ID

#### `get_weaknesses_for_mitigation`
Find all weaknesses addressed by a specific mitigation.

**Parameters:**
- `mitigation_id` (string): Mitigation ID

#### `get_techniques_for_mitigation`
Find all techniques that benefit from a specific mitigation.

**Parameters:**
- `mitigation_id` (string): Mitigation ID

### Objective Management Tools

#### `list_objectives`
List all objectives from the current mapping.

**Parameters:** None

#### `get_techniques_for_objective`
Get all techniques associated with a specific objective.

**Parameters:**
- `objective_name` (string): Name of the objective

#### `list_available_mappings`
Show all available objective mapping files.

**Parameters:** None

#### `load_objective_mapping`
Switch to a different objective mapping (e.g., carrier.json, dfrws.json).

**Parameters:**
- `filename` (string): Mapping filename (e.g., "carrier.json")

### Bulk Retrieval Tools

#### Concise Format Tools
- `get_all_techniques_with_name_and_id` - All techniques with ID and name only
- `get_all_weaknesses_with_name_and_id` - All weaknesses with ID and name only  
- `get_all_mitigations_with_name_and_id` - All mitigations with ID and name only

#### Full Detail Tools (Use with caution - large data)
- `get_all_techniques_with_full_detail` - All techniques with complete details
- `get_all_weaknesses_with_full_detail` - All weaknesses with complete details
- `get_all_mitigations_with_full_detail` - All mitigations with complete details

## Usage Examples
<Pending>

## Data Configuration

The server automatically looks for the SOLVE-IT knowledge base in these locations:

1. `../solve-it-main/` (adjacent to server directory)
2. `./solve-it-main/` (in current directory)
3. Environment variable `SOLVE_IT_DATA_PATH`

Ensure your SOLVE-IT data directory contains:
- `data/solve-it.json` (default objective mapping)
- `data/techniques/` (technique JSON files)
- `data/weaknesses/` (weakness JSON files)
- `data/mitigations/` (mitigation JSON files)

## Performance Considerations

- **Search operations**: Typically complete in <5 seconds
- **Bulk operations**: May take <10 seconds for full detail retrievals
- **Individual lookups**: Near-instant response
- **Relationship queries**: Optimized for fast traversal

## Error Handling

The server provides comprehensive error handling:

- **Missing data**: Graceful fallback with helpful error messages
- **Invalid IDs**: Clear feedback on incorrect technique/weakness/mitigation IDs
- **Connection issues**: Automatic retry and timeout handling
- **Large datasets**: Memory-efficient processing with warnings

## Integration Examples

### Claude Desktop

```json
{
  "mcpServers": {
    "solveit": {
      "command": "python3",
      "args": ["/path/to/solve_it_mcp/src/server.py"],
      "cwd": "/path/to/solve_it_mcp"
    }
  }
}
```

## Security Features

- **Read-only access**: Server only reads from the knowledge base
- **Input validation**: All parameters validated with Pydantic schemas
- **Timeout protection**: Automatic timeouts for long-running operations
- **Memory limits**: Protection against excessive memory usage
- **Path validation**: Secure file path handling

## Development

### Running Tests

```bash
# Run integration tests with real SOLVE-IT data
python3 -m pytest solve_it_mcp/tests/integration/ -v

# Run unit tests
python3 -m pytest solve_it_mcp/tests/unit/ -v
```

## Troubleshooting

### Common Issues

**"Knowledge base not found"**
- Ensure SOLVE-IT data is in `../solve-it-main/` or set `SOLVE_IT_DATA_PATH`
- Verify the data directory contains `data/solve-it.json`

**"Technique/Weakness/Mitigation not found"**
- Check ID format (e.g., "T1001", "W1001", "M1001")
- Use `search` tool to find valid IDs

**"Mapping file not found"**
- Use `list_available_mappings` to see available files
- Ensure mapping files are in `data/` directory

## License

MIT License - See LICENSE file for details.

## Contributing

This server is part of the SOLVE-IT ecosystem. Contributions welcome through:

1. Issue reports for bugs or missing features
2. Pull requests for improvements
3. Documentation enhancements
4. Additional tool implementations

---

**Ready to investigate?** Start with `get_database_description` to explore the knowledge base, then use `search` to find relevant techniques for your investigation.
