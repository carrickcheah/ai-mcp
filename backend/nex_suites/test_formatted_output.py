#!/usr/bin/env python3
"""
Test formatted output display for PERKESO receipt.
Shows the markdown in a readable format.
"""

import asyncio
from pathlib import Path
from tools.document_converter import DocumentConverter
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.panel import Panel

console = Console()

async def display_formatted_output():
    """Display formatted output for PERKESO PDF."""
    downloads = Path.home() / "Downloads"
    pdf_file = downloads / "EIS_2025E0004343673.pdf"

    if not pdf_file.exists():
        console.print("[red]PDF file not found![/red]")
        return

    console.print("\n[bold cyan]Converting PERKESO Receipt...[/bold cyan]\n")

    # Get markdown output
    markdown_result = await DocumentConverter.convert(str(pdf_file), "markdown")

    # Display as formatted markdown
    console.print(Panel.fit(
        Markdown(markdown_result),
        title="[bold]Formatted Receipt[/bold]",
        border_style="cyan"
    ))

    # Also show the clean table format
    console.print("\n[bold cyan]Clean Table View:[/bold cyan]\n")

    # Parse the markdown to extract table data
    lines = markdown_result.split('\n')

    # Create a Rich table
    table = Table(title="RESIT RASMI - PERKESO", show_header=False, box=None)
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value", style="white")

    # Extract table rows from markdown
    for line in lines:
        if line.startswith('|') and not line.startswith('|---'):
            parts = line.split('|')
            if len(parts) >= 3:
                field = parts[1].strip()
                value = parts[2].strip()
                if field and field != "Field":  # Skip header
                    table.add_row(field, value)

    console.print(table)

    # Show text format as well
    console.print("\n[bold cyan]Plain Text Format:[/bold cyan]\n")
    text_result = await DocumentConverter.convert(str(pdf_file), "text")

    # Display in a panel for clean appearance
    console.print(Panel(
        text_result,
        title="[bold]Text Output[/bold]",
        border_style="green"
    ))

if __name__ == "__main__":
    # Install rich if not available
    try:
        import rich
    except ImportError:
        import subprocess
        print("Installing rich for better display...")
        subprocess.run(["uv", "add", "rich"])

    asyncio.run(display_formatted_output())