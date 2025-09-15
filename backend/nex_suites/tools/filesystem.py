"""
Filesystem operations with roots security.
Follows cli_root's security patterns for safe file access.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import Context
from tools.document_converter import DocumentConverter
from core.utils import file_url_to_path


async def is_path_allowed(requested_path: Path, ctx: Context) -> bool:
    """Check if path is within allowed roots."""
    roots_result = await ctx.session.list_roots()
    client_roots = roots_result.roots

    # Resolve to absolute path
    requested_path = requested_path.resolve()

    if not requested_path.exists():
        return False

    # If it's a file, check its parent directory
    if requested_path.is_file():
        requested_path = requested_path.parent

    # Check if path is within any allowed root
    for root in client_roots:
        root_path = file_url_to_path(root.uri)
        try:
            # This will raise ValueError if not relative
            requested_path.relative_to(root_path)
            return True
        except ValueError:
            continue

    return False


async def list_roots(ctx: Context) -> List[str]:
    """
    List all directories that are accessible to this server.
    These are the root directories where files can be read from or written to.
    """
    try:
        roots_result = await ctx.session.list_roots()
        client_roots = roots_result.roots

        root_paths = []
        for root in client_roots:
            path = file_url_to_path(root.uri)
            root_paths.append(str(path))

        return root_paths
    except Exception as e:
        ctx.info(f"Error listing roots: {str(e)}")
        return []


async def read_directory(path: str, *, ctx: Context) -> List[Dict[str, Any]]:
    """Read directory contents. Path must be within one of the client's roots."""
    requested_path = Path(path).resolve()

    # Validate access
    if not await is_path_allowed(requested_path, ctx):
        raise ValueError(f"Error: can only read directories within a root. Path '{path}' is not allowed.")

    if not requested_path.is_dir():
        raise ValueError(f"Error: '{path}' is not a directory")

    files = []
    try:
        for entry in requested_path.iterdir():
            file_info = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
                "path": str(entry)
            }

            if entry.is_file():
                file_info["extension"] = entry.suffix.lower()
                file_info["size"] = entry.stat().st_size

            files.append(file_info)

        # Sort: directories first, then files
        files.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

    except PermissionError:
        raise ValueError(f"Error: Permission denied accessing '{path}'")

    return files


async def find_documents(
    pattern: str,
    root_path: Optional[str] = None,
    *,
    ctx: Context
) -> List[Dict[str, Any]]:
    """
    Find documents matching a pattern within allowed roots.
    Pattern can be a glob pattern like '*.pdf' or a partial filename.
    """
    results = []
    roots = await list_roots(ctx)

    if root_path:
        # Search in specific root
        if root_path not in roots:
            raise ValueError(f"Path '{root_path}' is not an allowed root")
        search_paths = [Path(root_path)]
    else:
        # Search in all roots
        search_paths = [Path(r) for r in roots]

    for root in search_paths:
        try:
            # Use glob to find matching files
            if '*' in pattern or '?' in pattern:
                # It's a glob pattern
                matches = root.glob(f"**/{pattern}")
            else:
                # It's a partial filename, search for it
                matches = root.glob(f"**/*{pattern}*")

            for match in matches:
                if match.is_file():
                    # Check if it's a supported document type
                    ext = match.suffix.lower()[1:]
                    if ext in DocumentConverter.SUPPORTED_INPUT_FORMATS:
                        results.append({
                            "path": str(match),
                            "name": match.name,
                            "extension": ext,
                            "size": match.stat().st_size,
                            "root": str(root)
                        })
        except Exception as e:
            ctx.info(f"Error searching in {root}: {str(e)}")

    return results


async def convert_document(
    input_path: str,
    output_format: str = "markdown",
    *,
    ctx: Context
) -> str:
    """Convert document to specified format with roots validation."""
    input_file = Path(input_path).resolve()

    # Security check - ensure file is within allowed roots
    if not await is_path_allowed(input_file, ctx):
        raise ValueError(f"Access denied: '{input_path}' is not within allowed roots")

    if not input_file.is_file():
        raise ValueError(f"Error: '{input_path}' is not a file")

    # Validate output format
    if output_format not in DocumentConverter.OUTPUT_FORMATS:
        raise ValueError(f"Invalid output format '{output_format}'. Must be one of: {DocumentConverter.OUTPUT_FORMATS}")

    try:
        # Log progress
        ctx.info(f"Starting conversion of {input_file.name} to {output_format}")

        # Perform conversion
        result = await DocumentConverter.convert(str(input_file), output_format)

        ctx.info(f"Successfully converted {input_file.name}")

        return result

    except Exception as e:
        error_msg = f"Failed to convert {input_file.name}: {str(e)}"
        ctx.info(error_msg)
        raise ValueError(error_msg)


async def save_conversion(
    input_path: str,
    output_path: str,
    output_format: str = "markdown",
    *,
    ctx: Context
) -> str:
    """
    Convert document and save to file.
    Both input and output paths must be within allowed roots.
    """
    output_file = Path(output_path).resolve()

    # Check output path is allowed
    if not await is_path_allowed(output_file.parent, ctx):
        raise ValueError(f"Access denied: Cannot write to '{output_path}'")

    # Perform conversion
    result = await convert_document(input_path, output_format, ctx=ctx)

    # Save to file
    try:
        output_file.write_text(result, encoding='utf-8')
        ctx.info(f"Saved conversion to {output_file}")
        return f"Successfully converted and saved to {output_file}"
    except Exception as e:
        raise ValueError(f"Failed to save file: {str(e)}")