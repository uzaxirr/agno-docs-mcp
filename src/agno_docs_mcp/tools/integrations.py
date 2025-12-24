"""Integrations tool for Agno framework."""

from pathlib import Path

from ..utils.paths import get_docs_base_dir, list_directory, resolve_doc_path
from ..utils.content import format_file_content, format_directory_listing
from ..utils.search import search_documents


# Valid integration types
INTEGRATION_TYPES = {
    "database": "integrations/database",
    "vectordb": "integrations/vectordb",
    "models": "integrations/models",
    "toolkits": "integrations/toolkits",
    "memory": "integrations/memory",
    "observability": "integrations/observability",
    "discord": "integrations/discord",
    "testing": "integrations/testing",
}


def agno_integrations(
    integration_type: str,
    name: str | None = None,
    query_keywords: list[str] | None = None
) -> str:
    """Get Agno integration documentation.

    Access guides for integrating Agno with databases, vector stores,
    LLM providers, and toolkits.

    Args:
        integration_type: Type of integration - one of: database, vectordb, models,
                          toolkits, memory, observability, discord, testing
        name: Optional specific integration name (e.g., "postgres", "pinecone", "openai")
        query_keywords: Optional keywords to search within the integration type

    Returns:
        Integration documentation as markdown
    """
    base_dir = get_docs_base_dir()
    integrations_dir = base_dir / "integrations"

    if not integrations_dir.exists():
        return (
            "Integrations documentation not found.\n"
            "Run `python -m agno_docs_mcp.prepare` to prepare docs."
        )

    # Normalize integration type
    type_lower = integration_type.lower().strip()

    if type_lower not in INTEGRATION_TYPES:
        available_types = ", ".join(INTEGRATION_TYPES.keys())
        return (
            f"Unknown integration type: `{integration_type}`\n\n"
            f"**Available types:** {available_types}\n\n"
            f"Example: `integration_type=\"database\", name=\"postgres\"`"
        )

    type_path = INTEGRATION_TYPES[type_lower]
    type_dir = base_dir / type_path

    if not type_dir.exists():
        return f"Integration type `{integration_type}` not found in docs."

    # If specific name provided, get that integration
    if name:
        name_lower = name.lower().strip()

        # Try to find the file
        possible_paths = [
            type_dir / f"{name_lower}.mdx",
            type_dir / f"{name_lower}.md",
            type_dir / name_lower / "index.mdx",
            type_dir / name_lower,
        ]

        for path in possible_paths:
            if path.exists():
                if path.is_file():
                    rel_path = f"{type_path}/{path.name}"
                    return format_file_content(path, rel_path)
                else:
                    rel_path = f"{type_path}/{name_lower}"
                    return f"## {integration_type.title()}: {name}\n\n" + \
                           format_directory_listing(path, rel_path)

        # Not found - show available integrations
        contents = list_directory(type_dir)
        available = [f.replace(".mdx", "").replace(".md", "") for f in contents.files]
        available.extend(d.rstrip("/") for d in contents.dirs)

        return (
            f"Integration `{name}` not found in `{integration_type}`.\n\n"
            f"**Available {integration_type} integrations:**\n" +
            "\n".join(f"- `{a}`" for a in sorted(available))
        )

    # No specific name - list all integrations of this type
    results = [
        f"## {integration_type.title()} Integrations\n",
        f"*Location: `{type_path}/`*\n",
    ]

    contents = list_directory(type_dir)

    # List available integrations
    integrations: list[str] = []
    for file_name in contents.files:
        int_name = file_name.replace(".mdx", "").replace(".md", "")
        integrations.append(int_name)

    for dir_name in contents.dirs:
        int_name = dir_name.rstrip("/")
        integrations.append(int_name)

    if integrations:
        results.append(f"**Available integrations ({len(integrations)}):**\n")
        for int_name in sorted(integrations):
            results.append(f"- `{int_name}`")

        results.append(f"\nUse `name=\"{integrations[0]}\"` to get specific integration docs.")
    else:
        results.append("No integrations found in this category.")

    # If keywords provided, search for matches
    if query_keywords:
        matched = search_documents(query_keywords, type_dir, limit=10)
        if matched:
            results.append("\n**Matching your keywords:**")
            for m in matched:
                results.append(f"- `{type_path}/{m}`")

    return "\n".join(results)


def get_integrations_description() -> str:
    """Get the tool description."""
    types = ", ".join(INTEGRATION_TYPES.keys())
    return f"""Get Agno integration documentation.

Access guides for integrating with databases, vector stores, LLM providers, and toolkits.

**Integration types:** {types}

**Database integrations include:** PostgreSQL, MongoDB, SQLite, MySQL, Redis, DynamoDB,
Firestore, and many more (22+ databases, including async variants).

**Vector DB integrations include:** Pinecone, Qdrant, Chroma, Weaviate, Milvus,
LanceDB, and more (22+ vector stores).

**Model providers:** OpenAI, Anthropic, Google, Azure, AWS Bedrock, and more.

**Usage:**
- `integration_type="database"` - List all database integrations
- `integration_type="database", name="postgres"` - Get PostgreSQL integration docs
- `integration_type="vectordb", name="pinecone"` - Get Pinecone integration docs"""
