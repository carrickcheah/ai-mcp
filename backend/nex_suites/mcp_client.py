import sys
import asyncio
from typing import Optional, Any, Callable, List
from contextlib import AsyncExitStack
from pathlib import Path
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from mcp.types import LoggingMessageNotificationParams, Root, ListRootsResult, ErrorData
from mcp.shared.context import RequestContext
from pydantic import FileUrl


class MCPClient:
    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
        roots: Optional[List[str]] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._roots = self._create_roots(roots) if roots else []
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

    def _create_roots(self, root_paths: List[str]) -> List[Root]:
        """Convert path strings to Root objects."""
        roots = []
        for path in root_paths:
            p = Path(path).resolve()
            file_url = FileUrl(f"file://{p}")
            roots.append(Root(uri=file_url, name=p.name or "Root"))
        return roots

    async def _handle_list_roots(
        self, context: RequestContext["ClientSession", None]
    ) -> ListRootsResult | ErrorData:
        """Callback for when server requests roots."""
        return ListRootsResult(roots=self._roots)

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        
        # Define logging callback to handle server log messages
        async def logging_callback(params: LoggingMessageNotificationParams):
            # Print log messages with appropriate prefix
            level = params.level if hasattr(params, 'level') else 'info'
            message = params.data if hasattr(params, 'data') else str(params)
            print(f"  [{level.upper()}] {message}")
        
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        _stdio, _write = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(
                _stdio,
                _write,
                logging_callback=logging_callback,
                list_roots_callback=self._handle_list_roots if self._roots else None,
            )
        )
        await self._session.initialize()

    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized or cache not populated. Call connect_to_server first."
            )
        return self._session

    async def list_tools(self) -> list[types.Tool]:
        """Return a list of tools defined by the MCP server."""
        result = await self.session().list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Call a particular tool and return the result."""
        
        # Define progress callback to display progress updates
        async def print_progress_callback(
            progress: float, total: float | None, message: str | None
        ):
            if total is not None:
                percentage = (progress / total) * 100
                print(f"  [PROGRESS] {progress:.0f}/{total:.0f} ({percentage:.1f}%)")
            else:
                print(f"  [PROGRESS] {progress}")
            if message:
                print(f"  [PROGRESS] {message}")
        
        # Call tool with progress callback for visual feedback
        result = await self.session().call_tool(
            tool_name, 
            tool_input,
            progress_callback=print_progress_callback
        )
        return result

    async def list_prompts(self) -> list[types.Prompt]:
        # TODO: Return a list of prompts defined by the MCP server
        return []

    async def get_prompt(self, prompt_name, args: dict[str, str]):
        # TODO: Get a particular prompt defined by the MCP server
        return []

    async def read_resource(self, uri: str) -> Any:
        # TODO: Read a resource, parse the contents and return it
        return []

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# For testing
async def main():
    async with MCPClient(
        # If using Python without UV, update command to 'python' and remove "run" from args.
        command="uv",
        args=["run", "mcp_server.py"],
    ) as _client:
        pass


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
