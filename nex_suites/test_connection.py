"""Test MariaDB database connection."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import aiomysql
from config import db_config


async def test_connection():
    """Test MariaDB connection using configuration."""
    print("Testing MariaDB connection...")
    print(f"Host: {db_config.host}")
    print(f"Port: {db_config.port}")
    print(f"Database: {db_config.database}")
    print(f"User: {db_config.user}")
    print("-" * 40)
    
    try:
        # Create connection
        conn = await aiomysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            db=db_config.database,
            autocommit=True
        )
        
        print("✅ Successfully connected to MariaDB!")
        
        # Test query
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT VERSION()")
            version = await cursor.fetchone()
            print(f"MariaDB Version: {version[0]}")
            
            # List tables
            await cursor.execute("SHOW TABLES")
            tables = await cursor.fetchall()
            print(f"\nTables in database '{db_config.database}':")
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  (No tables found)")
        
        conn.close()
        print("\n✅ Connection test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease check:")
        print("1. MariaDB server is running")
        print("2. Environment variables are correctly set:")
        print("   - DB_HOST")
        print("   - DB_PORT")
        print("   - DB_NAME")
        print("   - DB_USER")
        print("   - DB_PASSWORD")
        print("3. User has access to the specified database")
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    sys.exit(0 if result else 1)