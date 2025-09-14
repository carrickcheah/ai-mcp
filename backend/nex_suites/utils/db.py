"""Database utilities for Nex Suites."""

import aiomysql
import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager
from config import db_config

logger = logging.getLogger(__name__)

# MCP-compliant timeout (2 minutes default)
DEFAULT_TIMEOUT = 120  # seconds


class DatabaseConnection:
    """MariaDB connection manager using aiomysql."""
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 database: Optional[str] = None):
        """
        Initialize database connection parameters.
        Uses config defaults if parameters not provided.
        
        Args:
            host: Database host
            port: Database port
            user: Database user
            password: Database password
            database: Database name
        """
        self.host = host or db_config.host
        self.port = port or db_config.port
        self.user = user or db_config.user
        self.password = password or db_config.password
        self.database = database or db_config.database
        self.connection = None
        self.pool = None
    
    async def connect(self, timeout: int = DEFAULT_TIMEOUT):
        """Establish database connection with timeout.
        
        Args:
            timeout: Connection timeout in seconds
        """
        try:
            logger.debug(
                f"Connecting to MariaDB at {self.host}:{self.port}/{self.database}"
            )
            self.connection = await asyncio.wait_for(
                aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    autocommit=True,
                    charset='utf8mb4'
                ),
                timeout=timeout
            )
            logger.debug("Successfully connected to MariaDB")
        except asyncio.TimeoutError:
            logger.error(f"Connection timeout after {timeout} seconds")
            raise ConnectionError(f"Database connection timeout ({timeout}s)")
        except aiomysql.Error as e:
            logger.exception("Database connection failed")
            raise ConnectionError(f"Database connection failed: {e}")
        except (OSError, ConnectionError) as e:
            logger.exception("Network error during connection")
            raise ConnectionError(f"Network error: {e}")
    
    async def create_pool(
        self, 
        minsize: int = 1, 
        maxsize: int = 10,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """Create connection pool for better performance.
        
        Args:
            minsize: Minimum pool size
            maxsize: Maximum pool size  
            timeout: Connection timeout in seconds
        """
        try:
            logger.debug(
                f"Creating connection pool (min={minsize}, max={maxsize})"
            )
            self.pool = await asyncio.wait_for(
                aiomysql.create_pool(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    db=self.database,
                    minsize=minsize,
                    maxsize=maxsize,
                    autocommit=True,
                    charset='utf8mb4'
                ),
                timeout=timeout
            )
            logger.debug("Connection pool created successfully")
        except asyncio.TimeoutError:
            logger.error(f"Pool creation timeout after {timeout} seconds")
            raise ConnectionError(f"Pool creation timeout ({timeout}s)")
        except aiomysql.Error as e:
            logger.exception("Failed to create connection pool")
            raise ConnectionError(f"Pool creation failed: {e}")
    
    async def disconnect(self):
        """Close database connection."""
        try:
            if self.connection:
                self.connection.close()
                logger.debug("Disconnected from database")
                self.connection = None
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
                logger.debug("Connection pool closed")
                self.pool = None
        except aiomysql.Error:
            # Log at debug level for cleanup errors
            logger.debug("Error during disconnect (non-critical)")
    
    async def execute(self, query: str, params: Optional[Union[tuple, list]] = None) -> int:
        """
        Execute a database query (INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query to execute
            params: Optional query parameters as tuple or list
        
        Returns:
            Number of affected rows
        """
        cursor = None
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    async with conn.cursor() as cursor:
                        await cursor.execute(query, params)
                        return cursor.rowcount
            elif self.connection:
                cursor = await self.connection.cursor()
                await cursor.execute(query, params)
                return cursor.rowcount
            else:
                raise RuntimeError("No database connection available")
        except aiomysql.Error as e:
            logger.exception("Database query execution failed")
            raise
        except RuntimeError:
            raise
        finally:
            if cursor and not self.pool:
                await cursor.close()
    
    async def fetch_one(self, query: str, params: Optional[Union[tuple, list]] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row from database.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters as tuple or list
        
        Returns:
            Single row as dictionary or None
        """
        cursor = None
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(query, params)
                        return await cursor.fetchone()
            elif self.connection:
                cursor = await self.connection.cursor(aiomysql.DictCursor)
                await cursor.execute(query, params)
                return await cursor.fetchone()
            else:
                raise RuntimeError("No database connection available")
        except aiomysql.Error as e:
            logger.exception("Failed to fetch single row")
            raise
        except RuntimeError:
            raise
        finally:
            if cursor and not self.pool:
                await cursor.close()
    
    async def fetch_all(self, query: str, params: Optional[Union[tuple, list]] = None) -> List[Dict[str, Any]]:
        """
        Fetch all rows from database.
        
        Args:
            query: SQL query to execute
            params: Optional query parameters as tuple or list
        
        Returns:
            List of rows as dictionaries
        """
        cursor = None
        try:
            if self.pool:
                async with self.pool.acquire() as conn:
                    async with conn.cursor(aiomysql.DictCursor) as cursor:
                        await cursor.execute(query, params)
                        return await cursor.fetchall()
            elif self.connection:
                cursor = await self.connection.cursor(aiomysql.DictCursor)
                await cursor.execute(query, params)
                return await cursor.fetchall()
            else:
                raise RuntimeError("No database connection available")
        except aiomysql.Error as e:
            logger.exception("Failed to fetch rows")
            raise
        except RuntimeError:
            raise
        finally:
            if cursor and not self.pool:
                await cursor.close()


@asynccontextmanager
async def get_db_connection(host: Optional[str] = None,
                           port: Optional[int] = None,
                           user: Optional[str] = None,
                           password: Optional[str] = None,
                           database: Optional[str] = None):
    """
    Context manager for database connections.
    Uses config defaults if parameters not provided.
    
    Args:
        host: Database host
        port: Database port  
        user: Database user
        password: Database password
        database: Database name
    
    Yields:
        DatabaseConnection instance
    """
    conn = DatabaseConnection(host, port, user, password, database)
    try:
        await conn.connect()
        yield conn
    finally:
        await conn.disconnect()


@asynccontextmanager
async def get_db_pool(minsize: int = 1, 
                     maxsize: int = 10,
                     host: Optional[str] = None,
                     port: Optional[int] = None,
                     user: Optional[str] = None,
                     password: Optional[str] = None,
                     database: Optional[str] = None):
    """
    Context manager for database connection pool.
    Uses config defaults if parameters not provided.
    
    Args:
        minsize: Minimum pool size
        maxsize: Maximum pool size
        host: Database host
        port: Database port
        user: Database user
        password: Database password
        database: Database name
    
    Yields:
        DatabaseConnection instance with pool
    """
    conn = DatabaseConnection(host, port, user, password, database)
    try:
        await conn.create_pool(minsize, maxsize)
        yield conn
    finally:
        await conn.disconnect()


# Helper functions for common queries
async def insert_record(
    conn: DatabaseConnection, 
    table_name: str, 
    data: Dict[str, Any]
) -> int:
    """
    Insert a record into a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        data: Record data as dict
    
    Returns:
        Last inserted row ID
    """
    if not data:
        raise ValueError("Cannot insert empty record")
    
    columns = list(data.keys())
    values = list(data.values())
    placeholders = ', '.join(['%s'] * len(values))
    columns_str = ', '.join(f"`{col}`" for col in columns)
    
    query = f"""
        INSERT INTO `{table_name}` ({columns_str})
        VALUES ({placeholders})
    """
    
    try:
        cursor = None
        if conn.pool:
            async with conn.pool.acquire() as connection:
                async with connection.cursor() as cursor:
                    await cursor.execute(query, values)
                    return cursor.lastrowid
        elif conn.connection:
            cursor = await conn.connection.cursor()
            await cursor.execute(query, values)
            return cursor.lastrowid
        else:
            raise RuntimeError("No database connection available")
    except aiomysql.Error as e:
        logger.exception(f"Failed to insert into {table_name}")
        raise
    finally:
        if cursor and not conn.pool:
            await cursor.close()


async def update_record(
    conn: DatabaseConnection, 
    table_name: str, 
    record_id: Any, 
    data: Dict[str, Any],
    id_column: str = "id"
) -> int:
    """
    Update a record in a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        record_id: Record identifier value
        data: Updated data as dict
        id_column: Name of ID column (default: "id")
    
    Returns:
        Number of affected rows
    """
    if not data:
        raise ValueError("Cannot update with empty data")
    
    set_clauses = ', '.join(
        f"`{col}` = %s" for col in data.keys()
    )
    values = list(data.values()) + [record_id]
    
    query = f"""
        UPDATE `{table_name}`
        SET {set_clauses}
        WHERE `{id_column}` = %s
    """
    
    try:
        return await conn.execute(query, values)
    except aiomysql.Error as e:
        logger.exception(f"Failed to update {table_name}")
        raise


async def delete_record(
    conn: DatabaseConnection, 
    table_name: str, 
    record_id: Any,
    id_column: str = "id"
) -> int:
    """
    Delete a record from a table.
    
    Args:
        conn: Database connection
        table_name: Name of the table
        record_id: Record identifier value
        id_column: Name of ID column (default: "id")
    
    Returns:
        Number of deleted rows
    """
    query = f"""
        DELETE FROM `{table_name}`
        WHERE `{id_column}` = %s
    """
    
    try:
        return await conn.execute(query, (record_id,))
    except aiomysql.Error as e:
        logger.exception(f"Failed to delete from {table_name}")
        raise


async def table_exists(
    conn: DatabaseConnection,
    table_name: str
) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        conn: Database connection
        table_name: Name of the table
    
    Returns:
        True if table exists, False otherwise
    """
    query = """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s
        AND table_name = %s
    """
    
    try:
        result = await conn.fetch_one(
            query, 
            (conn.database, table_name)
        )
        return result['COUNT(*)'] > 0 if result else False
    except aiomysql.Error as e:
        logger.exception(f"Failed to check if table {table_name} exists")
        raise