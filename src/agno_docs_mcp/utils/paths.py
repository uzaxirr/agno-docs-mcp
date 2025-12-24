"""Path resolution and validation utilities."""

import os
from pathlib import Path
from typing import NamedTuple


class DirectoryContents(NamedTuple):
    """Contents of a directory."""
    dirs: list[str]
    files: list[str]


def get_package_root() -> Path:
    """Get the root directory of this package."""
    return Path(__file__).parent.parent.parent.parent


def get_docs_base_dir() -> Path:
    """Get the base directory for preprocessed documentation."""
    return get_package_root() / ".docs" / "raw"


def get_snippets_dir() -> Path:
    """Get the directory for code snippets."""
    return get_package_root() / ".docs" / "snippets"


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Check if target_path is safely within base_dir (no path traversal).

    Args:
        base_dir: The base directory that should contain target_path
        target_path: The path to validate

    Returns:
        True if target_path is within base_dir, False otherwise
    """
    try:
        resolved_base = base_dir.resolve()
        resolved_target = target_path.resolve()
        return str(resolved_target).startswith(str(resolved_base))
    except (OSError, ValueError):
        return False


def resolve_doc_path(doc_path: str, base_dir: Path | None = None) -> tuple[Path, bool]:
    """Resolve a documentation path to a full filesystem path.

    Args:
        doc_path: Relative documentation path (e.g., "basics/agents/overview")
        base_dir: Base directory for docs (defaults to .docs/raw/)

    Returns:
        Tuple of (resolved_path, is_valid)
    """
    if base_dir is None:
        base_dir = get_docs_base_dir()

    # Normalize the path
    clean_path = doc_path.strip("/").strip()

    # Handle empty path
    if not clean_path:
        return base_dir, True

    # Resolve the full path
    full_path = base_dir / clean_path

    # Security check
    if not is_safe_path(base_dir, full_path):
        return full_path, False

    # Try to find the file (with or without .mdx extension)
    if full_path.exists():
        return full_path, True

    # Try adding .mdx extension
    mdx_path = full_path.with_suffix(".mdx")
    if mdx_path.exists():
        return mdx_path, True

    # Try adding .md extension
    md_path = full_path.with_suffix(".md")
    if md_path.exists():
        return md_path, True

    return full_path, False


def list_directory(dir_path: Path) -> DirectoryContents:
    """List contents of a directory.

    Args:
        dir_path: Path to the directory

    Returns:
        DirectoryContents with sorted lists of subdirectories and MDX files
    """
    dirs: list[str] = []
    files: list[str] = []

    if not dir_path.is_dir():
        return DirectoryContents(dirs=[], files=[])

    try:
        for entry in dir_path.iterdir():
            if entry.is_dir():
                dirs.append(entry.name + "/")
            elif entry.is_file() and entry.suffix in (".mdx", ".md"):
                files.append(entry.name)
    except PermissionError:
        pass

    return DirectoryContents(
        dirs=sorted(dirs),
        files=sorted(files)
    )


def find_nearest_directory(doc_path: str, base_dir: Path | None = None) -> tuple[Path, str]:
    """Find the nearest existing parent directory for a non-existent path.

    Args:
        doc_path: The documentation path that wasn't found
        base_dir: Base directory for docs

    Returns:
        Tuple of (nearest_existing_directory, relative_path_from_base)
    """
    if base_dir is None:
        base_dir = get_docs_base_dir()

    parts = doc_path.strip("/").split("/")

    while parts:
        test_path = base_dir / "/".join(parts)
        if test_path.is_dir():
            return test_path, "/".join(parts)
        parts.pop()

    return base_dir, ""


def get_available_paths(base_dir: Path | None = None) -> str:
    """Get a formatted list of available top-level paths.

    Args:
        base_dir: Base directory for docs

    Returns:
        Formatted string listing available paths
    """
    if base_dir is None:
        base_dir = get_docs_base_dir()

    if not base_dir.exists():
        return "Documentation not found. Run 'python -m agno_docs_mcp.prepare' to prepare docs."

    contents = list_directory(base_dir)

    lines = ["Available top-level paths:", ""]

    if contents.dirs:
        lines.append("Directories:")
        lines.extend(f"- {d}" for d in contents.dirs)
        lines.append("")

    if contents.files:
        lines.append("Files:")
        lines.extend(f"- {f}" for f in contents.files)

    return "\n".join(lines)
