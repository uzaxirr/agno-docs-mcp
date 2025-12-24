"""Content reading and formatting utilities."""

import re
from pathlib import Path
from typing import Any

import yaml

from .paths import list_directory, DirectoryContents, get_docs_base_dir


# Cache for resolved snippets to avoid re-reading
_snippet_cache: dict[str, str] = {}


def get_snippets_dir() -> Path:
    """Get the path to the snippets directory."""
    # Snippets are stored in .docs/snippets/ (sibling to .docs/raw/)
    base_dir = get_docs_base_dir()  # This returns .docs/raw
    return base_dir.parent / "snippets"


def resolve_snippets(content: str, max_depth: int = 3) -> str:
    """Resolve <Snippet file="..."/> tags by inlining the snippet content.

    Args:
        content: MDX content that may contain Snippet tags
        max_depth: Maximum recursion depth for nested snippets

    Returns:
        Content with snippets resolved/inlined
    """
    if max_depth <= 0:
        return content

    # Pattern to match <Snippet file="filename.mdx" /> or <Snippet file="filename.mdx"/>
    snippet_pattern = re.compile(
        r'<Snippet\s+file=["\']([^"\']+)["\']\s*/?>',
        re.IGNORECASE
    )

    def replace_snippet(match: re.Match) -> str:
        snippet_file = match.group(1)

        # Check cache first
        if snippet_file in _snippet_cache:
            return _snippet_cache[snippet_file]

        # Find snippet in snippets directory
        snippets_dir = get_snippets_dir()
        snippet_path = snippets_dir / snippet_file

        if not snippet_path.exists():
            # Try with .mdx extension if not provided
            if not snippet_file.endswith('.mdx'):
                snippet_path = snippets_dir / f"{snippet_file}.mdx"

        if snippet_path.exists():
            try:
                snippet_content = snippet_path.read_text(encoding="utf-8")
                # Parse frontmatter from snippet (remove it)
                _, snippet_body = parse_frontmatter(snippet_content)
                # Recursively resolve any nested snippets
                resolved = resolve_snippets(snippet_body.strip(), max_depth - 1)
                _snippet_cache[snippet_file] = resolved
                return resolved
            except (OSError, UnicodeDecodeError):
                return f"<!-- Snippet {snippet_file} could not be loaded -->"
        else:
            return f"<!-- Snippet {snippet_file} not found -->"

    return snippet_pattern.sub(replace_snippet, content)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from MDX content.

    Args:
        content: Raw MDX file content

    Returns:
        Tuple of (frontmatter_dict, remaining_content)
    """
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return {}, content

    frontmatter_str = content[3:end_match.start() + 3]
    remaining_content = content[end_match.end() + 3:]

    try:
        frontmatter = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError:
        frontmatter = {}

    return frontmatter, remaining_content


def read_mdx_file(file_path: Path, resolve_snippet_tags: bool = True) -> tuple[dict[str, Any], str]:
    """Read an MDX file and parse its frontmatter.

    Args:
        file_path: Path to the MDX file
        resolve_snippet_tags: Whether to resolve <Snippet> tags

    Returns:
        Tuple of (frontmatter_dict, content)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)

        # Resolve snippet references
        if resolve_snippet_tags:
            body = resolve_snippets(body)

        return frontmatter, body
    except (OSError, UnicodeDecodeError) as e:
        return {}, f"Error reading file: {e}"


def format_directory_listing(
    dir_path: Path,
    relative_path: str,
    include_file_contents: bool = True
) -> str:
    """Format a directory listing as markdown.

    Args:
        dir_path: Path to the directory
        relative_path: Relative path for display
        include_file_contents: Whether to include contents of all files

    Returns:
        Formatted markdown string
    """
    contents = list_directory(dir_path)

    lines = [
        f"Directory contents of `{relative_path or '/'}`:",
        "",
    ]

    if contents.dirs:
        lines.append("**Subdirectories:**")
        lines.extend(f"- `{d}`" for d in contents.dirs)
        lines.append("")
    else:
        lines.append("No subdirectories.")
        lines.append("")

    if contents.files:
        lines.append("**Files in this directory:**")
        lines.extend(f"- `{f}`" for f in contents.files)
        lines.append("")
    else:
        lines.append("No files in this directory.")
        lines.append("")

    if include_file_contents and contents.files:
        lines.append("---")
        lines.append("")
        lines.append("**Contents of all files in this directory:**")
        lines.append("")

        for file_name in contents.files:
            file_path = dir_path / file_name
            frontmatter, content = read_mdx_file(file_path)

            title = frontmatter.get("title", file_name)
            lines.append(f"## {title}")
            lines.append(f"*File: `{relative_path}/{file_name}`*")
            lines.append("")
            lines.append(content.strip())
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def format_file_content(file_path: Path, relative_path: str) -> str:
    """Format a single file's content as markdown.

    Args:
        file_path: Path to the file
        relative_path: Relative path for display

    Returns:
        Formatted markdown string
    """
    frontmatter, content = read_mdx_file(file_path)

    title = frontmatter.get("title", file_path.name)
    description = frontmatter.get("description", "")

    lines = [
        f"# {title}",
        f"*File: `{relative_path}`*",
    ]

    if description:
        lines.append(f"*{description}*")

    lines.append("")
    lines.append(content.strip())

    return "\n".join(lines)


def format_not_found_error(
    doc_path: str,
    nearest_path: str,
    contents: DirectoryContents,
    suggestions: list[str] | None = None
) -> str:
    """Format a helpful error message when a path is not found.

    Args:
        doc_path: The path that wasn't found
        nearest_path: The nearest existing parent directory
        contents: Contents of the nearest directory
        suggestions: Optional list of suggested paths based on keywords

    Returns:
        Formatted error message
    """
    lines = [
        f"Path `{doc_path}` not found.",
        "",
    ]

    if nearest_path:
        lines.append(f"Here are the available paths in `{nearest_path}`:")
    else:
        lines.append("Here are the available top-level paths:")
    lines.append("")

    if contents.dirs:
        lines.append("**Directories:**")
        prefix = f"{nearest_path}/" if nearest_path else ""
        lines.extend(f"- `{prefix}{d}`" for d in contents.dirs)
        lines.append("")

    if contents.files:
        lines.append("**Files:**")
        prefix = f"{nearest_path}/" if nearest_path else ""
        lines.extend(f"- `{prefix}{f}`" for f in contents.files)
        lines.append("")

    if suggestions:
        lines.append("---")
        lines.append("")
        lines.append("**Suggested paths based on your query:**")
        lines.extend(f"- `{s}`" for s in suggestions[:10])

    return "\n".join(lines)
