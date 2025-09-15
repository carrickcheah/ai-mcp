"""
Centralized roots management for MCP file operations.
Handles command-line argument parsing and root directory validation.
"""

from pathlib import Path
from typing import Optional, List
import argparse
import os


class RootsManager:
    """Centralized roots management following Single Responsibility Principle."""

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse command-line arguments for roots and other configs."""
        parser = argparse.ArgumentParser(
            description="MCP Chat with document conversion capabilities"
        )

        # Roots argument
        parser.add_argument(
            '--roots',
            nargs='+',
            type=str,
            help='Root directories for file access (e.g., --roots /Documents /Downloads)',
            default=[]
        )

        # Future extensibility
        parser.add_argument(
            '--model',
            type=str,
            help='Override Claude model from .env',
            default=None
        )

        parser.add_argument(
            '--servers',
            nargs='+',
            type=str,
            help='Additional MCP servers to connect',
            default=[]
        )

        # Logging control
        parser.add_argument(
            '--verbose', '-v',
            action='count',
            default=0,
            help='Increase verbosity (-v, -vv, -vvv)'
        )

        return parser.parse_args()

    @staticmethod
    def validate_roots(root_paths: List[str]) -> List[Path]:
        """Validate and resolve root paths."""
        validated_roots = []

        for path_str in root_paths:
            path = Path(path_str).resolve()

            if not path.exists():
                print(f"Warning: Root path does not exist: {path_str}")
                continue

            if not path.is_dir():
                print(f"Warning: Root path is not a directory: {path_str}")
                continue

            validated_roots.append(path)
            print(f"✓ Added root: {path}")

        if root_paths and not validated_roots:
            print("Warning: No valid root directories provided. File operations will be limited.")

        return validated_roots

    @staticmethod
    def setup_logging(verbosity: int, existing_level: int = None):
        """Configure logging based on verbosity."""
        import logging

        # Map verbosity to logging levels
        levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        level = levels[min(verbosity, len(levels) - 1)]

        # Only change if more verbose than existing
        if existing_level is None or level < existing_level:
            logging.basicConfig(level=level)

            # Adjust specific loggers
            if verbosity < 2:
                logging.getLogger("mcp").setLevel(logging.ERROR)
                logging.getLogger("utils.db").setLevel(logging.ERROR)
                logging.getLogger("mcp.server").setLevel(logging.ERROR)