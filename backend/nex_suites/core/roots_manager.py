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
    def get_default_roots() -> List[str]:
        """Get sensible default root directories based on OS and what exists."""
        home = Path.home()
        defaults = []

        # Common user directories - check if they exist
        common_dirs = ['Downloads', 'Documents', 'Desktop']
        for dir_name in common_dirs:
            dir_path = home / dir_name
            if dir_path.exists() and dir_path.is_dir():
                defaults.append(str(dir_path))

        # Add temp directory if it exists
        if Path('/tmp').exists():
            defaults.append('/tmp')
        elif Path('/var/tmp').exists():
            defaults.append('/var/tmp')

        # If no defaults found, at least add home directory
        if not defaults:
            defaults.append(str(home))

        return defaults

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """Parse command-line arguments for roots and other configs."""
        parser = argparse.ArgumentParser(
            description="MCP Chat with document conversion capabilities"
        )

        # Roots argument - now optional with smart defaults
        parser.add_argument(
            '--roots',
            nargs='+',
            type=str,
            help='Root directories for file access (optional, uses common directories if not specified)',
            default=None  # Changed from [] to None to detect when not provided
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

        args = parser.parse_args()

        # Apply smart defaults if no roots provided
        if args.roots is None:
            args.roots = RootsManager.get_default_roots()
            print("\n" + "="*60)
            print("No --roots specified. Using default directories:")
            for root in args.roots:
                # Make paths more readable
                display_path = root.replace(str(Path.home()), "~")
                print(f"  • {display_path}")
            print("="*60 + "\n")
            print("To use different directories, restart with:")
            print(f"  python main.py --roots /your/path1 /your/path2")
            print()

        return args

    @staticmethod
    def validate_roots(root_paths: List[str]) -> List[Path]:
        """Validate and resolve root paths."""
        validated_roots = []
        show_details = len(root_paths) <= 3  # Only show details for custom roots

        for path_str in root_paths:
            path = Path(path_str).resolve()

            if not path.exists():
                print(f"Warning: Root path does not exist: {path_str}")
                continue

            if not path.is_dir():
                print(f"Warning: Root path is not a directory: {path_str}")
                continue

            validated_roots.append(path)
            if show_details:
                display_path = str(path).replace(str(Path.home()), "~")
                print(f"  ✓ Added root: {display_path}")

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