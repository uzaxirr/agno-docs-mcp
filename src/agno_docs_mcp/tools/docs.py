"""Core documentation tool for Agno framework."""

from pathlib import Path

from ..utils.paths import (
    get_docs_base_dir,
    resolve_doc_path,
    list_directory,
    find_nearest_directory,
    get_available_paths,
)
from ..utils.content import (
    format_directory_listing,
    format_file_content,
    format_not_found_error,
)
from ..utils.search import get_matching_paths, search_documents


def agno_docs(paths: list[str], query_keywords: list[str] | None = None) -> str:
    """Get Agno documentation by path.

    Navigate and search the core Agno documentation including guides for
    agents, teams, workflows, tools, memory, knowledge, and more.

    Use paths to explore the documentation structure. Start with broad paths
    like "basics/" or "basics/agents/" to discover available content.

    Args:
        paths: One or more documentation paths to fetch (e.g., ["basics/agents/overview"])
        query_keywords: Optional keywords from user query to find relevant content

    Returns:
        Documentation content as markdown
    """
    base_dir = get_docs_base_dir()

    if not base_dir.exists():
        return (
            "Documentation not prepared. Run `python -m agno_docs_mcp.prepare` first.\n\n"
            "This will copy the Agno documentation to the local .docs/ directory."
        )

    results: list[str] = []

    for doc_path in paths:
        result = _fetch_single_path(doc_path, query_keywords, base_dir)
        results.append(result)

    return "\n\n---\n\n".join(results)


def _fetch_single_path(
    doc_path: str,
    query_keywords: list[str] | None,
    base_dir: Path
) -> str:
    """Fetch content for a single documentation path."""
    resolved_path, is_valid = resolve_doc_path(doc_path, base_dir)

    # Security violation
    if not is_valid and resolved_path != base_dir:
        # Check if it's a security issue vs just not found
        from ..utils.paths import is_safe_path
        if not is_safe_path(base_dir, resolved_path):
            return f"## {doc_path}\n\nInvalid path."

    # Path exists - return content
    if resolved_path.exists():
        relative_path = doc_path.strip("/") or "/"

        if resolved_path.is_dir():
            content = format_directory_listing(resolved_path, relative_path)

            # Add keyword-based suggestions if provided
            if query_keywords:
                suggestions = get_matching_paths(doc_path, query_keywords, base_dir)
                if suggestions:
                    content += f"\n\n{suggestions}"

            return f"## {doc_path}\n\n{content}"
        else:
            content = format_file_content(resolved_path, relative_path)
            return content

    # Path not found - provide helpful error
    nearest_dir, nearest_path = find_nearest_directory(doc_path, base_dir)
    contents = list_directory(nearest_dir)

    # Get keyword-based suggestions
    suggestions = []
    if query_keywords:
        suggestions = search_documents(query_keywords, base_dir, limit=10)

    error_content = format_not_found_error(doc_path, nearest_path, contents, suggestions)
    return f"## {doc_path}\n\n{error_content}"


def get_docs_description() -> str:
    """Get the tool description including available paths."""
    available = get_available_paths()
    return f"""Get Agno documentation by path.

Navigate the documentation structure to find guides on agents, teams, workflows,
tools, memory, knowledge, and other core Agno features.

**Usage Tips:**
- Start with directory paths like "basics/" or "basics/agents/" to explore structure
- Use specific paths like "basics/agents/overview" for detailed content
- Provide query_keywords to get content-based suggestions
- Check both general docs AND reference docs for complete information

**Important directories:**
- `basics/` - Core concepts (agents, teams, workflows, tools, memory, knowledge)
- `get-started/` - Quickstart and introduction
- `faq/` - Frequently asked questions
- `how-to/` - Installation, migration, and guides

{available}

IMPORTANT: Be concise with answers. Include code examples. Mention file paths for reference.
If packages need to be installed, show the pip/uv command."""
