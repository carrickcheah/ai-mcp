import asyncio
import sys
import os
import logging

# Configure logging BEFORE importing other modules
# Suppress all INFO logs except from our tools
logging.basicConfig(level=logging.ERROR)
logging.getLogger("server").setLevel(logging.ERROR)
logging.getLogger("mcp").setLevel(logging.ERROR)
logging.getLogger("utils.db").setLevel(logging.ERROR)
logging.getLogger("mcp.server").setLevel(logging.ERROR)
logging.getLogger("mcp.server.fastmcp").setLevel(logging.ERROR)

from dotenv import load_dotenv
from contextlib import AsyncExitStack  # Manages multiple async context managers for MCP clients

from mcp_client import MCPClient
from core.claude import Claude

from core.cli_chat import CliChat
from core.cli import CliApp

load_dotenv()

# Anthropic Config - Required environment variables for Claude API
claude_model = os.getenv("CLAUDE_MODEL", "")  # e.g., "claude-3-opus-20240229"
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")  # Your Anthropic API key

# Check working or not - Fail fast if required config is missing
assert claude_model, "Error: CLAUDE_MODEL cannot be empty. Update .env"
assert anthropic_api_key, (
"Error: ANTHROPIC_API_KEY cannot be empty. Update .env"
)


async def main():
    # Initialize Claude service with configured model
    claude_service = Claude(model=claude_model)

    # Get additional MCP server scripts from command-line arguments
    server_scripts = sys.argv[1:]  # e.g., python main.py server2.py server3.py
    clients = {}  # Dictionary to store all MCP client connections

    # Choose between uv or python for launching the default MCP server
    command, args = (
        ("uv", ["run", "mcp_server.py"])  # Use uv package manager
        if os.getenv("USE_UV", "0") == "1"
        else ("python", ["mcp_server.py"])  # Use standard Python
    )

    # AsyncExitStack ensures all clients are properly cleaned up on exit
    async with AsyncExitStack() as stack:
        # Primary document server - provides document-related tools/resources/prompts
        doc_client = await stack.enter_async_context(
            MCPClient(command=command, args=args)
        )
        clients["doc_client"] = doc_client  # Special key for document operations

        # Connect to additional MCP servers passed as command-line arguments
        for i, server_script in enumerate(server_scripts):
            client_id = f"client_{i}_{server_script}"  # Unique ID for each additional client
            client = await stack.enter_async_context(
                MCPClient(command="uv", args=["run", server_script])
            )
            clients[client_id] = client  # Add to clients dictionary

        # Initialize chat system with document support (@ mentions, slash commands)
        chat = CliChat(
            doc_client=doc_client,  # Primary client for document operations
            clients=clients,  # All connected MCP clients (including doc_client)
            claude_service=claude_service,  # Anthropic API wrapper
        )

        # Create and run the terminal interface
        cli = CliApp(chat)  # Terminal UI for user interaction
        await cli.initialize()  # Set up the CLI interface
        await cli.run()  # Start the interactive chat loop


if __name__ == "__main__":
    # Windows requires ProactorEventLoop for subprocess handling
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    # Launch the async main function
    asyncio.run(main())




# APPLICATION FLOW:
# ==================
# 1. STARTUP PHASE:
#    - Load environment variables from .env file
#    - Validate required config (CLAUDE_MODEL, ANTHROPIC_API_KEY)
#    - Initialize Claude service with API credentials
#
# 2. MCP SERVER CONNECTIONS:
#    - Launch primary mcp_server.py subprocess (document server)
#    - Connect doc_client via stdio transport (JSON-RPC 2.0)
#    - Launch any additional MCP servers from command-line args
#    - Store all clients in dictionary for tool aggregation
#
# 3. CHAT INITIALIZATION:
#    - Create CliChat with doc_client for document operations
#    - Pass all clients for tool/resource/prompt access
#    - Initialize CLI terminal interface
#
# 4. RUNTIME MESSAGE FLOW:
#    User Input → CliChat Processing:
#      a) Check for /commands → doc_client.get_prompt()
#      b) Check for @mentions → doc_client.read_resource() 
#      c) Build message with context
#    ↓
#    Send to Claude with tools from all MCP servers:
#      - ToolManager.get_all_tools() aggregates capabilities
#      - Claude decides which tools to use
#    ↓
#    Tool Execution Loop (if needed):
#      - ToolManager routes to correct MCP client
#      - Client sends JSON-RPC request to server
#      - Server executes operation (read/edit docs, etc.)
#      - Results return to Claude for next decision
#    ↓
#    Final Response → Display to User → Wait for next input
#
# 5. CLEANUP ON EXIT:
#    - AsyncExitStack closes all client connections
#    - Terminates all MCP server subprocesses
#    - Releases all resources gracefully
#
# KEY ARCHITECTURE POINTS:
# - Async/await throughout for concurrent operations
# - Multi-server support via clients dictionary
# - Tool aggregation from all connected servers
# - Document-centric with special doc_client handling
# - Clean resource management with context managers
