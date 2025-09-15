#!/usr/bin/env python3
"""
Test that rich markdown rendering works in the chat interface.
"""

import asyncio
from pathlib import Path

# Test by simulating what the chat would return
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Simulate a markdown response from the AI
test_markdown = """# RESIT RASMI

No. Resit : 2025E0004343673

---

## PERKESO

| Tarikh Masa | 09/09/2025 09:03:48 PM |
|-------------|-----|
| Tarikh Bayaran | 09/09/2025 |
| Jenis Bayaran | 1. Caruman Bulanan(ECR092250182222-08/2025)(RM28.80)<br>2. Tunggakan Caruman-<br>3. Kekurangan Caruman- |
| Kod Majikan | B3901000913X |
| Nama Majikan | ASIAJAYA TILING CONSTRUCTION SDN BHD |
| Kaedah Bayaran | Online Portal |
| FPX Transaksi ID | 2509092103370667 |
| Bank | Malayan Banking Berhad (M2U) |
| Jumlah Bayaran | RM28.80 |
| Catatan | CP_090925_032282 |

"Resit ini adalah cetakan komputer dan tandatangan tidak diperlukan."
"""

def test_rich_rendering():
    """Test how the response would be rendered."""
    print("\n" + "="*60)
    print("Testing Rich Markdown Rendering in Chat")
    print("="*60 + "\n")

    print("Simulating chat response with rich markdown:\n")

    # This is what the updated cli.py will do
    console.print(Panel(
        Markdown(test_markdown),
        title="[bold cyan]Response[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))

    print("\n" + "="*60)
    print("✅ Rich markdown rendering configured!")
    print("The chat will now display all markdown responses with formatting.")
    print("="*60)

if __name__ == "__main__":
    test_rich_rendering()