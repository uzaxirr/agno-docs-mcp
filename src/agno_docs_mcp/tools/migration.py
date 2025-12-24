"""Migration and troubleshooting tool for Agno framework."""

from pathlib import Path

from ..utils.paths import get_docs_base_dir, list_directory
from ..utils.content import read_mdx_file
from ..utils.search import search_documents


# Available migration/troubleshooting topics
MIGRATION_TOPICS = {
    "v2-migration": "how-to/v2-migration.mdx",
    "workflows-migration": "how-to/workflows-migration.mdx",
    "installation": "how-to/install.mdx",
    "contributing": "how-to/contribute.mdx",
    "cursor-rules": "how-to/cursor-rules.mdx",
    "changelog": "how-to/v2-changelog.mdx",
}

# FAQ topics
FAQ_TOPICS = {
    "agentos-connection": "faq/agentos-connection.mdx",
    "docker-connection": "faq/could-not-connect-to-docker.mdx",
    "environment": "faq/environment-variables.mdx",
    "openai-key": "faq/openai-key-request-for-other-models.mdx",
    "rbac-auth": "faq/rbac-auth-failed.mdx",
    "structured-outputs": "faq/structured-outputs.mdx",
    "switching-models": "faq/switching-models.mdx",
    "tpm": "faq/tpm-issues.mdx",
    "workflow-vs-team": "faq/When-to-use-a-Workflow-vs-a-Team-in-Agno.mdx",
    "tableplus": "faq/connecting-to-tableplus.mdx",
}


def agno_migration(
    topic: str | None = None,
    faq_topic: str | None = None,
    query_keywords: list[str] | None = None
) -> str:
    """Get migration guides, FAQs, and troubleshooting documentation.

    Access guides for migrating to new Agno versions, installation help,
    and answers to frequently asked questions.

    Args:
        topic: Migration topic - one of: v2-migration, workflows-migration,
               installation, contributing, cursor-rules, changelog
        faq_topic: FAQ topic - one of: agentos-connection, docker-connection,
                   environment, openai-key, rbac-auth, structured-outputs,
                   switching-models, tpm, workflow-vs-team, tableplus
        query_keywords: Optional keywords to search migration/FAQ docs

    Returns:
        Migration or FAQ documentation as markdown
    """
    base_dir = get_docs_base_dir()
    howto_dir = base_dir / "how-to"
    faq_dir = base_dir / "faq"

    # Handle specific migration topic
    if topic:
        topic_lower = topic.lower().strip()

        if topic_lower not in MIGRATION_TOPICS:
            available = ", ".join(MIGRATION_TOPICS.keys())
            return (
                f"Unknown migration topic: `{topic}`\n\n"
                f"**Available topics:** {available}\n\n"
                f"For FAQs, use `faq_topic` parameter instead."
            )

        file_path = base_dir / MIGRATION_TOPICS[topic_lower]
        if file_path.exists():
            frontmatter, content = read_mdx_file(file_path)
            title = frontmatter.get("title", topic.replace("-", " ").title())

            return f"# {title}\n*File: `{MIGRATION_TOPICS[topic_lower]}`*\n\n{content}"
        else:
            return f"Migration document for `{topic}` not found."

    # Handle specific FAQ topic
    if faq_topic:
        faq_lower = faq_topic.lower().strip()

        if faq_lower not in FAQ_TOPICS:
            available = ", ".join(FAQ_TOPICS.keys())
            return (
                f"Unknown FAQ topic: `{faq_topic}`\n\n"
                f"**Available FAQs:** {available}"
            )

        file_path = base_dir / FAQ_TOPICS[faq_lower]
        if file_path.exists():
            frontmatter, content = read_mdx_file(file_path)
            title = frontmatter.get("title", faq_topic.replace("-", " ").title())

            return f"# FAQ: {title}\n*File: `{FAQ_TOPICS[faq_lower]}`*\n\n{content}"
        else:
            return f"FAQ document for `{faq_topic}` not found."

    # Search by keywords
    if query_keywords:
        results = ["## Search Results\n"]

        # Search how-to directory
        if howto_dir.exists():
            howto_matches = search_documents(query_keywords, howto_dir, limit=5)
            if howto_matches:
                results.append("**Migration/How-To Docs:**")
                for m in howto_matches:
                    results.append(f"- `how-to/{m}`")
                results.append("")

        # Search FAQ directory
        if faq_dir.exists():
            faq_matches = search_documents(query_keywords, faq_dir, limit=5)
            if faq_matches:
                results.append("**FAQ Docs:**")
                for m in faq_matches:
                    results.append(f"- `faq/{m}`")

        if len(results) > 1:
            return "\n".join(results)
        else:
            return "No matching documents found for your keywords."

    # No specific topic - list all available
    results = [
        "## Migration & Troubleshooting\n",
        "Access guides for migrating Agno versions and troubleshooting common issues.\n",
        "### Migration Guides\n",
    ]

    for topic_name in sorted(MIGRATION_TOPICS.keys()):
        display_name = topic_name.replace("-", " ").title()
        results.append(f"- **{display_name}** - `topic=\"{topic_name}\"`")

    results.append("\n### Frequently Asked Questions\n")

    for faq_name in sorted(FAQ_TOPICS.keys()):
        display_name = faq_name.replace("-", " ").title()
        results.append(f"- **{display_name}** - `faq_topic=\"{faq_name}\"`")

    results.append("\nUse `query_keywords` to search across all migration and FAQ docs.")

    return "\n".join(results)


def get_migration_description() -> str:
    """Get the tool description."""
    migration_topics = ", ".join(MIGRATION_TOPICS.keys())
    faq_topics = ", ".join(FAQ_TOPICS.keys())

    return f"""Get migration guides, FAQs, and troubleshooting documentation.

**Migration topics:** {migration_topics}

**FAQ topics:** {faq_topics}

**Usage:**
- `topic="v2-migration"` - Guide for migrating to Agno v2
- `topic="workflows-migration"` - Workflows migration guide
- `faq_topic="docker-connection"` - Docker connection troubleshooting
- `faq_topic="workflow-vs-team"` - When to use workflows vs teams
- `query_keywords=["error", "connection"]` - Search all migration/FAQ docs

Use this tool when users need help with:
- Upgrading from older Agno versions
- Installation issues
- Common errors and their solutions
- Best practices and FAQs"""
