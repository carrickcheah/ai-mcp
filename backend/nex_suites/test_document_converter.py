#!/usr/bin/env python3
"""
Test script for document conversion functionality.
Tests both direct converter and MCP integration.
"""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.document_converter import DocumentConverter


async def test_basic_conversion():
    """Test basic document converter functionality."""
    print("=" * 60)
    print("Testing Document Converter")
    print("=" * 60)

    # Test data - you can modify this to point to your test files
    test_cases = [
        {
            "description": "Test text extraction simulation",
            "text": """RESIT RASMI     No. Resit : 2025E0004343673

PERKESO

Tarikh Masa          :     09/09/2025 09:03:48 PM
Tarikh Bayaran       :     09/09/2025
Jenis Bayaran        :     1. Caruman Bulanan(ECR092250182222-08/2025)(RM28.80)
                           2. Tunggakan Caruman-
                           3. Kekurangan Caruman-
Kod Majikan          :     B3901000913X
Nama Majikan         :     ASIAJAYA TILING CONSTRUCTION SDN BHD
Kaedah Bayaran       :     Online Portal
FPX Transaksi ID     :     250909210337067
Bank                 :     Malayan Banking Berhad (M2U)
Jumlah Bayaran       :     RM28.80
Catatan              :     CP_090925_032282

"Resit ini adalah cetakan komputer dan tandatangan tidak diperlukan."
"""
        }
    ]

    for test in test_cases:
        print(f"\n{test['description']}")
        print("-" * 40)

        # Parse the receipt data
        parsed = DocumentConverter.parse_receipt_data(test["text"])
        print("\nParsed Data:")
        for key, value in parsed.items():
            if key != "payment_items":
                print(f"  {key}: {value}")

        if "payment_items" in parsed:
            print("  payment_items:")
            for item in parsed["payment_items"]:
                print(f"    {item['number']}. {item['description']}")

        # Test different output formats
        print("\n--- TEXT FORMAT ---")
        text_output = DocumentConverter.format_as_text({
            "parsed": parsed,
            "type": "image",
            "raw_text": test["text"]
        })
        print(text_output[:500] + "..." if len(text_output) > 500 else text_output)

        print("\n--- MARKDOWN FORMAT ---")
        markdown_output = DocumentConverter.format_as_markdown({
            "parsed": parsed,
            "type": "image",
            "filename": "test_receipt.png"
        })
        print(markdown_output[:500] + "..." if len(markdown_output) > 500 else markdown_output)

        print("\n--- JSON FORMAT (excerpt) ---")
        json_output = DocumentConverter.format_as_json({
            "parsed": parsed,
            "type": "image",
            "raw_text": test["text"],
            "filename": "test_receipt.png",
            "images": [{
                "name": "test_receipt.png",
                "width": 595,
                "height": 842
            }]
        })
        # Show first 600 chars of JSON
        print(json_output[:600] + "..." if len(json_output) > 600 else json_output)


async def test_mcp_integration():
    """Test MCP server integration."""
    print("\n" + "=" * 60)
    print("Testing MCP Integration")
    print("=" * 60)

    try:
        from mcp_client import MCPClient

        # Test with roots
        test_roots = ["/tmp", str(Path.home() / "Documents")]
        print(f"\nTesting with roots: {test_roots}")

        async with MCPClient(
            command="uv" if sys.platform != "win32" else "python",
            args=["run", "mcp_server.py"] if sys.platform != "win32" else ["mcp_server.py"],
            roots=test_roots
        ) as client:
            print("\n✓ MCP Client connected")

            # List available tools
            tools = await client.list_tools()
            doc_tools = [t for t in tools if "document" in t.name or "roots" in t.name]

            print(f"\n✓ Found {len(doc_tools)} document-related tools:")
            for tool in doc_tools:
                print(f"  - {tool.name}: {tool.description}")

            # Test list_roots tool
            print("\n✓ Testing list_roots tool:")
            result = await client.call_tool("list_roots", {})
            if result:
                print(f"  Roots: {result.content}")

    except Exception as e:
        print(f"\n✗ MCP Integration test failed: {e}")
        print("  This is expected if MCP server is not running")


async def main():
    """Run all tests."""
    print("Starting Document Converter Tests")
    print("=" * 60)

    # Test basic converter
    await test_basic_conversion()

    # Test MCP integration
    await test_mcp_integration()

    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)
    print("\nTo use with actual files:")
    print("  1. Start the app with roots: python main.py --roots /Documents /Downloads")
    print("  2. In chat, try:")
    print("     - 'List my root directories'")
    print("     - 'Find all PDF files'")
    print("     - 'Convert /path/to/receipt.pdf to markdown'")
    print("     - 'Convert the invoice image to JSON format'")


if __name__ == "__main__":
    asyncio.run(main())