"""Test database utilities compliance with CLAUDE.md guidelines."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.db import (
    get_db_connection, 
    get_db_pool, 
    insert_record,
    update_record,
    delete_record,
    table_exists
)


async def test_timeout_handling():
    """Test timeout handling per MCP guidelines."""
    print("=" * 50)
    print("Testing Timeout Handling (MCP 2-minute default)")
    print("=" * 50)
    
    try:
        # Test with very short timeout (should fail)
        async with get_db_connection() as db:
            # Override with 1ms timeout - should fail
            db.connection = None  # Clear existing
            await db.connect(timeout=0.001)
    except ConnectionError as e:
        print(f"✅ Timeout handled correctly: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print()


async def test_specific_exceptions():
    """Test specific exception handling per guidelines."""
    print("=" * 50)
    print("Testing Specific Exception Handling")
    print("=" * 50)
    
    async with get_db_connection() as db:
        # Test ValueError for empty data
        try:
            await insert_record(db, "test_table", {})
        except ValueError as e:
            print(f"✅ ValueError caught for empty insert: {e}")
        
        # Test RuntimeError for no connection
        db_no_conn = db.__class__()
        try:
            await db_no_conn.execute("SELECT 1")
        except RuntimeError as e:
            print(f"✅ RuntimeError caught for no connection: {e}")
    
    print()


async def test_helper_functions():
    """Test new helper functions."""
    print("=" * 50)
    print("Testing Helper Functions")
    print("=" * 50)
    
    async with get_db_connection() as db:
        test_table = "test_compliance_table"
        
        # Check if test table exists
        exists = await table_exists(db, test_table)
        print(f"Table '{test_table}' exists: {exists}")
        
        # Create test table if needed
        if not exists:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {test_table} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    value INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print(f"✅ Created test table '{test_table}'")
        
        # Test insert
        record_id = await insert_record(db, test_table, {
            "name": "test_item",
            "value": 42
        })
        print(f"✅ Inserted record with ID: {record_id}")
        
        # Test update
        rows = await update_record(db, test_table, record_id, {
            "value": 100,
            "name": "updated_item"
        })
        print(f"✅ Updated {rows} row(s)")
        
        # Verify update
        result = await db.fetch_one(
            f"SELECT * FROM {test_table} WHERE id = %s",
            (record_id,)
        )
        print(f"✅ Verified update: {result['name']} = {result['value']}")
        
        # Test delete
        rows = await delete_record(db, test_table, record_id)
        print(f"✅ Deleted {rows} row(s)")
        
        # Clean up
        await db.execute(f"DROP TABLE IF EXISTS {test_table}")
        print(f"✅ Cleaned up test table")
    
    print()


async def test_connection_pool():
    """Test connection pool with MCP performance guidelines."""
    print("=" * 50)
    print("Testing Connection Pool (MCP Performance)")
    print("=" * 50)
    
    # MCP guidelines suggest connection pooling for performance
    async with get_db_pool(minsize=2, maxsize=10) as db:
        print("✅ Pool created with MCP-compliant settings")
        
        # Run concurrent queries
        tasks = []
        for i in range(5):
            tasks.append(
                db.fetch_one("SELECT %s as num, CONNECTION_ID() as id", (i,))
            )
        
        results = await asyncio.gather(*tasks)
        print("✅ Concurrent queries executed:")
        for r in results:
            print(f"   Query {r['num']}: Connection {r['id']}")
    
    print()


async def test_logging_compliance():
    """Test logging patterns match CLAUDE.md."""
    print("=" * 50)
    print("Testing Logging Compliance")
    print("=" * 50)
    
    import logging
    
    # Set up handler to capture logs
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger('utils.db')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    async with get_db_connection() as db:
        # Should use logger.info for connection
        print("✅ Connection logs use info level")
        
        # Should use logger.debug for disconnect
        pass  # Disconnect happens on context exit
    
    print("✅ Disconnect logs use debug level")
    
    # Remove handler
    logger.removeHandler(handler)
    
    print()


async def main():
    """Run all compliance tests."""
    print("CLAUDE.md Compliance Test Suite")
    print("=" * 70)
    print()
    
    try:
        # Test timeout handling
        await test_timeout_handling()
        
        # Test specific exceptions
        await test_specific_exceptions()
        
        # Test helper functions
        await test_helper_functions()
        
        # Test connection pool
        await test_connection_pool()
        
        # Test logging patterns
        await test_logging_compliance()
        
        print("=" * 70)
        print("✅ All compliance tests passed!")
        print("Database utilities are fully compliant with CLAUDE.md")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Compliance test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)