"""API reference tool for Agno framework."""

from pathlib import Path

from ..utils.paths import (
    get_docs_base_dir,
    resolve_doc_path,
    list_directory,
    find_nearest_directory,
)
from ..utils.content import (
    format_directory_listing,
    format_file_content,
    format_not_found_error,
)
from ..utils.search import search_documents


# Valid reference topics
REFERENCE_TOPICS = [
    "agents",
    "teams",
    "workflows",
    "tools",
    "models",
    "memory",
    "knowledge",
    "storage",
    "hooks",
    "compression",
    "reasoning",
    "agent-os",
]


def agno_reference(topic: str, query_keywords: list[str] | None = None) -> str:
    """Get Agno API reference documentation.

    Access detailed API documentation including parameter references,
    configuration options, and method signatures for all Agno components.

    Args:
        topic: Reference topic - one of: agents, teams, workflows, tools, models,
               memory, knowledge, storage, hooks, compression, reasoning, agent-os
        query_keywords: Optional keywords to filter or search within the topic

    Returns:
        API reference documentation as markdown
    """
    base_dir = get_docs_base_dir()
    reference_dir = base_dir / "reference"

    if not reference_dir.exists():
        return (
            "Reference documentation not found.\n"
            "Run `python -m agno_docs_mcp.prepare` to prepare docs."
        )

    # Normalize topic
    topic_lower = topic.lower().strip().strip("/")

    # Check for valid topic
    if topic_lower not in REFERENCE_TOPICS and topic_lower != "":
        available_topics = ", ".join(REFERENCE_TOPICS)
        suggestions = search_documents(
            [topic_lower] + (query_keywords or []),
            reference_dir,
            limit=10
        )
        suggestion_text = ""
        if suggestions:
            suggestion_text = "\n\n**Suggested reference docs:**\n" + "\n".join(f"- `reference/{s}`" for s in suggestions)

        return (
            f"Unknown reference topic: `{topic}`\n\n"
            f"**Available topics:** {available_topics}\n\n"
            f"Use one of these topics, or browse with `topic=''` to see all categories."
            f"{suggestion_text}"
        )

    # Resolve the path
    if topic_lower:
        doc_path = f"reference/{topic_lower}"
    else:
        doc_path = "reference"

    resolved_path, _ = resolve_doc_path(doc_path, base_dir)

    if resolved_path.exists():
        if resolved_path.is_dir():
            content = format_directory_listing(resolved_path, doc_path)

            # Add keyword-based content if provided
            if query_keywords:
                keyword_results = search_documents(query_keywords, resolved_path, limit=10)
                if keyword_results:
                    content += "\n\n**Files matching your keywords:**\n"
                    content += "\n".join(f"- `{doc_path}/{r}`" for r in keyword_results)

            return f"## API Reference: {topic or 'All Topics'}\n\n{content}"
        else:
            return format_file_content(resolved_path, doc_path)

    # Topic directory not found - show what's available
    contents = list_directory(reference_dir)
    error = format_not_found_error(doc_path, "reference", contents)
    return f"## Reference: {topic}\n\n{error}"


def get_reference_description() -> str:
    """Get the tool description."""
    topics = ", ".join(REFERENCE_TOPICS)
    return f"""Get Agno API reference documentation.

Access detailed API docs including parameter references, configuration options,
and method signatures for all Agno components.

**Available topics:** {topics}

Use an empty topic string to browse all reference categories.

**Example usage:**
- `topic="agents"` - Agent API reference
- `topic="models"` - Model configuration reference (34+ model types)
- `topic="tools"` - Tool and toolkit API reference
- `topic=""` - List all reference categories

The reference section contains detailed parameter documentation that complements
the conceptual docs in basics/."""
