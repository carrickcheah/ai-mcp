"""Quick non-interactive test of MCP pairing."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_client import MCPClient


async def main():
    """Quick test of client-server pairing."""
    print("=" * 70)
    print("MCP CLIENT-SERVER PAIRING TEST")
    print("=" * 70)
    
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"]
    ) as client:
        # List tools
        tools = await client.list_tools()
        print(f"\n✅ Found {len(tools)} tools:")
        for t in tools:
            print(f"   - {t.name}")
        
        # Call get_sales
        print("\n📊 Testing get_sales with 'AUG':")
        result = await client.call_tool("get_sales", {"period": "AUG"})
        
        if result and hasattr(result, 'content'):
            # Show first 10 lines
            lines = str(result.content[0].text).split('\n')[:10]
            for line in lines:
                print(f"   {line}")
            print("   ... (truncated)")
        
        print("\n" + "=" * 70)
        print("✅ CLIENT-SERVER PAIRING SUCCESSFUL!")
        print("=" * 70)
        print("\n🎉 You can now run: uv run python main.py")
        print("   And ask Claude: 'Show me sales for August'")


if __name__ == "__main__":
    asyncio.run(main())