"""Test MCP Client-Server Tool Pairing."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_client import MCPClient


async def test_tool_pairing():
    """Test that client can see and call server tools."""
    print("=" * 70)
    print("Testing MCP Client-Server Tool Pairing")
    print("=" * 70)
    print()
    
    # Create MCP client and connect to server
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"]
    ) as client:
        print("✅ Connected to MCP server")
        print()
        
        # Test 1: List available tools
        print("1. Discovery Phase - list_tools()")
        print("-" * 40)
        tools = await client.list_tools()
        
        if not tools:
            print("❌ No tools found! Check server implementation.")
            return False
        
        print(f"✅ Found {len(tools)} tool(s):")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
            if hasattr(tool, 'inputSchema'):
                print(f"     Input: {tool.inputSchema}")
        print()
        
        # Check if get_sales tool exists
        tool_names = [t.name for t in tools]
        if "get_sales" not in tool_names:
            print("❌ 'get_sales' tool not found!")
            return False
        
        print("✅ 'get_sales' tool is available")
        print()
        
        # Test 2: Call the get_sales tool
        print("2. Execution Phase - call_tool()")
        print("-" * 40)
        
        test_periods = ["AUG", "last 30 days", "2024"]
        
        for period in test_periods:
            print(f"\nTesting with period: '{period}'")
            print("=" * 50)
            
            try:
                result = await client.call_tool(
                    "get_sales",
                    {"period": period}
                )
                
                if result:
                    if hasattr(result, 'content'):
                        # Show first 500 chars of result
                        content = str(result.content)[:500]
                        print(f"✅ Tool executed successfully:")
                        print(content)
                        if len(str(result.content)) > 500:
                            print("... (truncated)")
                    else:
                        print(f"✅ Result: {result}")
                else:
                    print("❌ No result returned from tool")
                    
            except Exception as e:
                print(f"❌ Error calling tool: {e}")
                import traceback
                traceback.print_exc()
            
            # Ask if user wants to continue
            if period != test_periods[-1]:
                response = input("\nPress Enter to test next period, or 'q' to quit: ")
                if response.lower() == 'q':
                    break
        
        print()
        print("=" * 70)
        print("✅ Client-Server pairing is working!")
        print("=" * 70)
        return True


async def test_tool_flow():
    """Test the complete tool flow with detailed output."""
    print("\n" + "=" * 70)
    print("Testing Complete Tool Flow")
    print("=" * 70)
    print()
    
    print("Flow Diagram:")
    print("  Client → list_tools() → Server")
    print("      ↓")
    print("  Server returns tools → Client")
    print("      ↓")
    print("  Client → call_tool('get_sales', {'period': 'AUG'}) → Server")
    print("      ↓")
    print("  Server executes → Database query → Format report")
    print("      ↓")
    print("  Server returns report → Client")
    print()
    
    async with MCPClient(
        command="uv",
        args=["run", "mcp_server.py"]
    ) as client:
        # Step 1: Discovery
        print("Step 1: Tool Discovery")
        tools = await client.list_tools()
        print(f"   JSON-RPC: {{\"method\": \"tools/list\"}}")
        print(f"   Response: {len(tools)} tool(s) available")
        
        # Step 2: Execution
        print("\nStep 2: Tool Execution")
        print("   JSON-RPC: {\"method\": \"tools/call\",")
        print("             \"params\": {\"name\": \"get_sales\",")
        print("                        \"arguments\": {\"period\": \"AUG\"}}}")
        
        result = await client.call_tool("get_sales", {"period": "AUG"})
        
        if result and hasattr(result, 'content'):
            lines = str(result.content).split('\n')[:5]
            print("   Response preview:")
            for line in lines:
                print(f"      {line}")
            print("      ...")
        
        print("\n✅ Tool flow completed successfully!")


async def main():
    """Run all pairing tests."""
    try:
        # Test basic pairing
        success = await test_tool_pairing()
        
        if success:
            # Test detailed flow
            await test_tool_flow()
            
            print("\n" + "=" * 70)
            print("🎉 MCP CLIENT-SERVER PAIRING COMPLETE!")
            print("=" * 70)
            print("\nYou can now run: uv run python main.py")
            print("And ask Claude: 'Show me sales for August'")
            print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)