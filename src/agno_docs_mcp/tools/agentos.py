"""AgentOS documentation tool for Agno framework."""

from pathlib import Path

from ..utils.paths import get_docs_base_dir, list_directory, resolve_doc_path
from ..utils.content import format_file_content, format_directory_listing
from ..utils.search import search_documents, get_matching_paths


def agno_agentos(
    path: str | None = None,
    query_keywords: list[str] | None = None
) -> str:
    """Get AgentOS runtime documentation.

    Access documentation for AgentOS, the production runtime for Agno agents.
    Covers deployment, API endpoints, security, middleware, and more.

    Args:
        path: Optional path within agent-os docs (e.g., "overview", "features/security")
        query_keywords: Optional keywords to search AgentOS documentation

    Returns:
        AgentOS documentation as markdown
    """
    base_dir = get_docs_base_dir()
    agentos_dir = base_dir / "agent-os"

    if not agentos_dir.exists():
        return (
            "AgentOS documentation not found.\n"
            "Run `python -m agno_docs_mcp.prepare` to prepare docs."
        )

    # If no path specified, show overview
    if not path:
        contents = list_directory(agentos_dir)

        result = [
            "## AgentOS Documentation\n",
            "AgentOS is the production runtime for Agno agents.\n",
            "*Location: `agent-os/`*\n",
            "**Available sections:**\n",
        ]

        for dir_name in contents.dirs:
            result.append(f"- `{dir_name}` directory")

        for file_name in contents.files:
            result.append(f"- `{file_name}`")

        result.append("\nUse `path=\"overview\"` or `path=\"features/\"` to explore sections.")

        # If keywords provided, search
        if query_keywords:
            matches = search_documents(query_keywords, agentos_dir, limit=10)
            if matches:
                result.append("\n**Matching your keywords:**")
                for m in matches:
                    result.append(f"- `agent-os/{m}`")

        return "\n".join(result)

    # Resolve the specific path
    doc_path = f"agent-os/{path.strip('/')}"
    resolved_path, is_valid = resolve_doc_path(doc_path, base_dir)

    if resolved_path.exists():
        if resolved_path.is_dir():
            content = format_directory_listing(resolved_path, doc_path)

            if query_keywords:
                suggestions = get_matching_paths(path, query_keywords, agentos_dir)
                if suggestions:
                    content += f"\n\n{suggestions}"

            return f"## AgentOS: {path}\n\n{content}"
        else:
            return format_file_content(resolved_path, doc_path)

    # Path not found
    contents = list_directory(agentos_dir)
    available = [d.rstrip("/") for d in contents.dirs]
    available.extend(f.replace(".mdx", "").replace(".md", "") for f in contents.files)

    result = [
        f"Path `{path}` not found in AgentOS docs.\n",
        "**Available paths:**\n",
    ]
    result.extend(f"- `{a}`" for a in sorted(available))

    if query_keywords:
        matches = search_documents(query_keywords, agentos_dir, limit=10)
        if matches:
            result.append("\n**Matching your keywords:**")
            for m in matches:
                result.append(f"- `agent-os/{m}`")

    return "\n".join(result)


def get_agentos_description() -> str:
    """Get the tool description."""
    return """Get AgentOS runtime documentation.

AgentOS is the production runtime for Agno agents, providing:
- **Deployment** - Deploy agents as API endpoints
- **API Endpoints** - RESTful API for agent interactions
- **Security** - Authentication, authorization, RBAC
- **Middleware** - Custom middleware support
- **MCP** - Model Context Protocol integration
- **Tracing** - Observability and debugging
- **Interfaces** - Web UI and other interfaces

**Usage:**
- No path - Overview of AgentOS documentation
- `path="overview"` - AgentOS introduction
- `path="features/"` - Browse features directory
- `path="features/security"` - Security documentation
- `path="usage/"` - Usage patterns and examples

Use this tool when users ask about deploying Agno agents to production,
setting up AgentOS, or configuring agent runtime features."""
