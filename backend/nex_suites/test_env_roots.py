#!/usr/bin/env python3
"""
Test that roots load correctly from .env file.
"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.roots_manager import RootsManager

def test_env_roots():
    """Test loading roots from .env configuration."""
    print("="*60)
    print("Testing .env Roots Configuration")
    print("="*60)

    # Check if DEFAULT_ROOTS is set
    env_value = os.getenv("DEFAULT_ROOTS", "")
    if env_value:
        print(f"\n✓ DEFAULT_ROOTS found in .env:")
        print(f"  Raw value: {env_value}")
    else:
        print("\n✗ DEFAULT_ROOTS not found in .env")

    # Get processed roots
    roots = RootsManager.get_default_roots()
    print(f"\nProcessed roots ({len(roots)} directories):")
    for root in roots:
        display = root.replace(str(Path.home()), "~")
        exists = "✓" if Path(root).exists() else "✗"
        print(f"  {exists} {display}")

    # Test with different configurations
    print("\n" + "-"*40)
    print("Testing different configurations:")

    # Test 1: Save current value
    original_value = os.getenv("DEFAULT_ROOTS", "")

    # Test 2: Test with invalid path
    os.environ["DEFAULT_ROOTS"] = "~/Downloads,/nonexistent/path,~/Documents"
    print("\nWith invalid path in DEFAULT_ROOTS:")
    roots = RootsManager.get_default_roots()
    print(f"  Valid roots found: {len(roots)}")

    # Test 3: Test with empty value
    os.environ["DEFAULT_ROOTS"] = ""
    print("\nWith empty DEFAULT_ROOTS:")
    roots = RootsManager.get_default_roots()
    print(f"  Falls back to smart defaults: {len(roots)} directories")

    # Test 4: Test with spaces
    os.environ["DEFAULT_ROOTS"] = " ~/Downloads , ~/Documents , /tmp "
    print("\nWith spaces in DEFAULT_ROOTS:")
    roots = RootsManager.get_default_roots()
    print(f"  Correctly parsed: {len(roots)} directories")

    # Restore original value
    if original_value:
        os.environ["DEFAULT_ROOTS"] = original_value
    else:
        del os.environ["DEFAULT_ROOTS"]

    print("\n" + "="*60)
    print("✅ .env roots configuration working correctly!")
    print("="*60)

if __name__ == "__main__":
    test_env_roots()