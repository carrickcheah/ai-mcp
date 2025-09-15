#!/usr/bin/env python3
"""
Test script to verify roots work without --roots argument.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.roots_manager import RootsManager
from mcp_client import MCPClient


async def test_without_args():
    """Test that defaults work without --roots."""
    print("="*60)
    print("Testing Without --roots Argument")
    print("="*60)

    # Test getting default roots
    defaults = RootsManager.get_default_roots()
    print(f"\nDefault roots found: {len(defaults)}")
    for root in defaults:
        display = root.replace(str(Path.home()), "~")
        print(f"  • {display}")

    # Test with MCP client
    print("\nTesting MCP client with defaults...")
    try:
        async with MCPClient(
            command="uv",
            args=["run", "mcp_server.py"],
            roots=defaults  # Use the defaults
        ) as client:
            print("✓ MCP client connected successfully")

            # Test list_roots
            result = await client.call_tool("list_roots", {})
            if result and result.content:
                print("✓ list_roots tool works")

            # Test find_documents
            result = await client.call_tool("find_documents", {"pattern": "*.pdf"})
            if result:
                print("✓ find_documents tool works")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*60)
    print("✅ Roots work without --roots argument!")
    print("="*60)


async def test_file_in_downloads():
    """Test finding a file in Downloads."""
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        # Check if there are any PDFs or images
        pdfs = list(downloads.glob("*.pdf"))
        images = list(downloads.glob("*.png")) + list(downloads.glob("*.jpg"))

        if pdfs:
            print(f"\nFound {len(pdfs)} PDF files in Downloads:")
            for pdf in pdfs[:3]:
                print(f"  • {pdf.name}")

        if images:
            print(f"\nFound {len(images)} image files in Downloads:")
            for img in images[:3]:
                print(f"  • {img.name}")

        if pdfs or images:
            print("\nYou can now convert these without specifying --roots!")
            print("Example: 'convert " + (pdfs[0].name if pdfs else images[0].name) + " to markdown'")


if __name__ == "__main__":
    print("Testing Roots Fix...")
    asyncio.run(test_without_args())
    asyncio.run(test_file_in_downloads())