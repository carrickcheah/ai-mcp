"""Test database utilities with actual MariaDB connection."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.db import DatabaseConnection, get_db_connection, get_db_pool


async def test_direct_connection():
    """Test direct database connection."""
    print("=" * 50)
    print("Testing Direct Connection")
    print("=" * 50)
    
    db = DatabaseConnection()
    try:
        await db.connect()
        print("✅ Connected successfully")
        
        # Test fetch_one
        result = await db.fetch_one("SELECT VERSION() as version")
        print(f"MariaDB Version: {result['version']}")
        
        # Test fetch_all - get first 5 tables
        tables = await db.fetch_all(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = %s LIMIT 5",
            (db.database,)
        )
        print(f"\nFirst 5 tables in '{db.database}':")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Test execute - create a test table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_connection (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("\n✅ Created test table")
        
        # Insert test data
        rows = await db.execute(
            "INSERT INTO test_connection (message) VALUES (%s)",
            ("Test from db utils",)
        )
        print(f"✅ Inserted {rows} row(s)")
        
        # Fetch the data back
        data = await db.fetch_all("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1")
        if data:
            print(f"✅ Retrieved: {data[0]}")
        
        # Clean up
        await db.execute("DROP TABLE IF EXISTS test_connection")
        print("✅ Cleaned up test table")
        
    finally:
        await db.disconnect()
        print("✅ Disconnected")


async def test_context_manager():
    """Test database connection with context manager."""
    print("\n" + "=" * 50)
    print("Testing Context Manager")
    print("=" * 50)
    
    async with get_db_connection() as db:
        print("✅ Connected via context manager")
        
        # Quick test query
        result = await db.fetch_one("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = %s", (db.database,))
        print(f"Total tables in database: {result['count']}")
    
    print("✅ Context manager closed connection")


async def test_connection_pool():
    """Test database connection pool."""
    print("\n" + "=" * 50)
    print("Testing Connection Pool")
    print("=" * 50)
    
    async with get_db_pool(minsize=2, maxsize=5) as db:
        print("✅ Created connection pool")
        
        # Run multiple queries concurrently
        tasks = []
        for i in range(5):
            tasks.append(db.fetch_one(f"SELECT {i} as num, CONNECTION_ID() as conn_id"))
        
        results = await asyncio.gather(*tasks)
        print("\nConcurrent queries results:")
        for result in results:
            print(f"  Query {result['num']}: Connection ID {result['conn_id']}")
    
    print("✅ Connection pool closed")


async def main():
    """Run all tests."""
    try:
        await test_direct_connection()
        await test_context_manager()
        await test_connection_pool()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)