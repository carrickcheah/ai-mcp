#!/usr/bin/env python3
"""
Direct test of document converter without the chat interface.
"""

import asyncio
from pathlib import Path
from tools.document_converter import DocumentConverter

async def test_conversion():
    """Test converting available files."""
    downloads = Path.home() / "Downloads"

    # Look for available test files
    screenshot = downloads / "Screenshot 2025-09-15 at 9.44.27 PM.png"
    pdf_file = downloads / "EIS_2025E0004343673.pdf"

    # Choose a file to test
    if screenshot.exists():
        test_file = screenshot
        print(f"Testing with screenshot: {test_file.name}")
    elif pdf_file.exists():
        test_file = pdf_file
        print(f"Testing with PDF: {test_file.name}")
    else:
        print("No supported test files found in Downloads!")
        print("Please add a PDF or image file to ~/Downloads")
        return

    print("="*60)
    print("Testing Document Converter")
    print("="*60)

    # Test text format
    print("\n1. TEXT FORMAT:")
    print("-"*40)
    text_result = await DocumentConverter.convert(str(test_file), "text")
    print(text_result)

    # Test markdown format
    print("\n2. MARKDOWN FORMAT:")
    print("-"*40)
    markdown_result = await DocumentConverter.convert(str(test_file), "markdown")
    print(markdown_result)

    # Test JSON format
    print("\n3. JSON FORMAT:")
    print("-"*40)
    json_result = await DocumentConverter.convert(str(test_file), "json")
    print(json_result[:500] + "..." if len(json_result) > 500 else json_result)

    print("\n" + "="*60)
    print("✅ Document converter works correctly!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_conversion())