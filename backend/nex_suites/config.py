"""Database configuration for Nex Suites."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabaseConfig:
    """MariaDB database configuration settings."""
    
    host: str
    port: int
    database: str
    user: str
    password: str
    
    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """
        Create configuration from environment variables.
        All variables are required - no defaults.
        """
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")
        database = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        
        # Validate all required environment variables are set
        if not host:
            raise ValueError("DB_HOST environment variable is required")
        if not port:
            raise ValueError("DB_PORT environment variable is required")
        if not database:
            raise ValueError("DB_NAME environment variable is required")
        if not user:
            raise ValueError("DB_USER environment variable is required")
        if not password:
            raise ValueError("DB_PASSWORD environment variable is required")
        
        return cls(
            host=host,
            port=int(port),
            database=database,
            user=user,
            password=password
        )
    
    @property
    def connection_string(self) -> str:
        """Get MariaDB connection string."""
        return f"mysql+mariadb://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# Global config instance
db_config = DatabaseConfig.from_env()