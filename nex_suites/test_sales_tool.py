"""Test the get_sales MCP tool."""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from tools.sales import get_sales, parse_period


async def test_period_parsing():
    """Test the period parsing function."""
    print("=" * 50)
    print("Testing Period Parsing")
    print("=" * 50)
    
    test_cases = [
        "AUG",
        "august", 
        "last 3 months",
        "last 30 days",
        "2024",
        "6 months",
        "1 year"
    ]
    
    for period in test_cases:
        start, end = parse_period(period)
        print(f"{period:20} -> {start.date()} to {end.date()}")
    
    print()


async def test_get_sales():
    """Test the get_sales function with different periods."""
    print("=" * 50)
    print("Testing get_sales Function")
    print("=" * 50)
    
    # Test different period formats
    test_periods = [
        "AUG",           # Specific month
        "last 30 days",  # Recent data
        "2024",          # Full year
        "last 3 months"  # Quarter
    ]
    
    for period in test_periods:
        print(f"\n{'='*70}")
        print(f"Testing period: {period}")
        print('='*70)
        
        try:
            result = await get_sales(period)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        
        # Ask if user wants to continue
        if period != test_periods[-1]:
            response = input("Press Enter to continue to next test, or 'q' to quit: ")
            if response.lower() == 'q':
                break


async def test_specific_period():
    """Interactive test - let user specify a period."""
    print("\n" + "=" * 50)
    print("Interactive Test - Enter Custom Period")
    print("=" * 50)
    
    print("\nExamples of valid periods:")
    print("  - Month names: 'AUG', 'September', 'dec'")
    print("  - Relative: 'last 3 months', 'last 30 days', '6 months'")
    print("  - Year: '2024', '2023'")
    
    while True:
        period = input("\nEnter period (or 'quit' to exit): ").strip()
        
        if period.lower() == 'quit':
            break
        
        if not period:
            continue
        
        try:
            print(f"\nFetching data for: {period}")
            result = await get_sales(period)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Run all tests."""
    print("MCP Sales Tool Test Suite")
    print("=" * 70)
    print()
    
    # Test period parsing
    await test_period_parsing()
    
    # Test with predefined periods
    response = input("Test with predefined periods? (y/n): ")
    if response.lower() == 'y':
        await test_get_sales()
    
    # Interactive test
    response = input("\nTest with custom periods? (y/n): ")
    if response.lower() == 'y':
        await test_specific_period()
    
    print("\n" + "=" * 70)
    print("Test completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()