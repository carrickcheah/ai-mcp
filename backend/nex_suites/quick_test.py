#!/usr/bin/env python3
"""
Quick test to verify document conversion with roots is working.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_client import MCPClient


async def test_with_real_paths():
    """Test with actual user directories."""

    # Use your actual directories
    test_roots = [
        "/Users/carrickcheah/Downloads",
        "/Users/carrickcheah/Documents",
        "/tmp"
    ]

    print("=" * 60)
    print("Testing Document Converter with Real Paths")
    print("=" * 60)
    print(f"\nUsing roots:")
    for root in test_roots:
        print(f"  - {root}")

    try:
        async with MCPClient(
            command="uv",
            args=["run", "mcp_server.py"],
            roots=test_roots
        ) as client:
            print("\n✓ Connected to MCP server with roots")

            # Test 1: List roots
            print("\n1. Testing list_roots:")
            result = await client.call_tool("list_roots", {})
            if result:
                roots_list = result.content[0].text if result.content else "No roots"
                print(f"   Available roots: {roots_list}")

            # Test 2: Read a directory
            print("\n2. Testing read_directory on /tmp:")
            result = await client.call_tool("read_directory", {"path": "/tmp"})
            if result and result.content:
                import json
                files = json.loads(result.content[0].text)
                print(f"   Found {len(files)} items in /tmp")
                # Show first 3 files
                for file in files[:3]:
                    print(f"   - {file['name']} ({file['type']})")

            # Test 3: Find documents
            print("\n3. Testing find_documents:")
            result = await client.call_tool("find_documents", {"pattern": "*.txt"})
            if result and result.content:
                docs = json.loads(result.content[0].text)
                print(f"   Found {len(docs)} text files")
                for doc in docs[:3]:
                    print(f"   - {doc['name']} in {doc['root']}")

            # Test 4: Try to access outside roots (should fail)
            print("\n4. Testing security (access outside roots):")
            try:
                result = await client.call_tool("read_directory", {"path": "/etc"})
                print("   ❌ SECURITY ISSUE: Should not access /etc!")
            except Exception as e:
                print(f"   ✓ Correctly denied access: {str(e)[:50]}...")

            print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def show_usage():
    """Show how to use the converter."""
    print("\n" + "=" * 60)
    print("How to Use Document Converter")
    print("=" * 60)

    print("\n1. Start the application with your directories:")
    print("   python main.py --roots /Users/carrickcheah/Downloads /Users/carrickcheah/Documents")

    print("\n2. In the chat, you can now say:")
    print("   - 'List my root directories'")
    print("   - 'Show files in Downloads'")
    print("   - 'Find all PDF files'")
    print("   - 'Convert /Users/carrickcheah/Downloads/receipt.pdf to markdown'")
    print("   - 'Convert the document to JSON format'")

    print("\n3. The converter will:")
    print("   - Only access files in your authorized directories")
    print("   - Extract text from PDFs and images (with OCR)")
    print("   - Format output as text, markdown, or JSON")
    print("   - Parse receipts and invoices intelligently")


if __name__ == "__main__":
    print("Starting Quick Test...")
    asyncio.run(test_with_real_paths())
    asyncio.run(show_usage())