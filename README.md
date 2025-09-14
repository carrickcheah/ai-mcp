# AI-MCP Project

A Model Context Protocol (MCP) implementation with web-based architecture.

## Project Structure

```
nex3_ai/
├── backend/        # MCP server and backend services
│   ├── nex_suites/ # Core MCP implementation
│   │   ├── tools/      # MCP tools
│   │   ├── resources/  # MCP resources
│   │   ├── prompts/    # MCP prompts
│   │   └── utils/      # Utilities
│   ├── pyproject.toml  # Python dependencies
│   └── uv.lock         # Lock file
└── frontend/       # Web frontend (React/TypeScript)
```

## Backend

The backend implements MCP (Model Context Protocol) with:
- FastMCP framework for server creation
- Tools for data operations
- Resources for data access
- Prompts for AI interactions

## Frontend

Web-based UI for interacting with the MCP backend (coming soon).

## Setup

### Backend Setup
```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Running the MCP Server
```bash
cd backend
uv run mcp dev nex_suites/mcp_server.py
```

## Development

This project uses:
- Python 3.12+ for backend
- FastMCP for MCP implementation
- uv for Python package management
- React/TypeScript for frontend (planned)