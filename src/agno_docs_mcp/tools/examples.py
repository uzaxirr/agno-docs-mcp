"""Code examples tool for Agno framework."""

from pathlib import Path

from ..utils.paths import get_docs_base_dir, get_snippets_dir, list_directory
from ..utils.content import read_mdx_file
from ..utils.search import search_documents, normalize_keywords


# Example categories that map to directory paths
EXAMPLE_CATEGORIES = {
    "agents": "basics/agents/usage",
    "teams": "basics/teams/usage",
    "workflows": "basics/workflows/usage",
    "tools": "basics/tools/usage",
    "memory": "basics/memory",
    "knowledge": "basics/knowledge",
    "models": "basics/models",
    "database": "basics/database",
    "evals": "basics/evals",
    "guardrails": "basics/guardrails",
    "hitl": "basics/hitl",
    "multimodal": "basics/multimodal",
    "reasoning": "basics/reasoning",
    "sessions": "basics/sessions",
    "tracing": "basics/tracing",
}


def agno_examples(
    category: str | None = None,
    query_keywords: list[str] | None = None
) -> str:
    """Get code examples and snippets for Agno framework.

    Access working code examples demonstrating how to use Agno features.
    Examples include agent creation, team workflows, tool usage, and more.

    Args:
        category: Optional category filter - one of: agents, teams, workflows,
                  tools, memory, knowledge, models, database, evals, guardrails,
                  hitl, multimodal, reasoning, sessions, tracing
        query_keywords: Optional keywords to search for specific examples

    Returns:
        Code examples as markdown
    """
    base_dir = get_docs_base_dir()
    snippets_dir = get_snippets_dir()

    if not base_dir.exists():
        return (
            "Examples not found. Run `python -m agno_docs_mcp.prepare` to prepare docs."
        )

    results: list[str] = []

    # If category specified, get examples from that category
    if category:
        category_lower = category.lower().strip()

        if category_lower not in EXAMPLE_CATEGORIES:
            available = ", ".join(sorted(EXAMPLE_CATEGORIES.keys()))
            return (
                f"Unknown category: `{category}`\n\n"
                f"**Available categories:** {available}\n\n"
                f"Use `category=None` with `query_keywords` to search all examples."
            )

        category_path = EXAMPLE_CATEGORIES[category_lower]
        category_dir = base_dir / category_path

        if category_dir.exists():
            results.append(f"## {category.title()} Examples\n")
            results.append(f"*Location: `{category_path}/`*\n")

            # List all examples in this category
            examples = _collect_examples_from_dir(category_dir, category_path)

            if query_keywords:
                # Filter by keywords
                keywords = normalize_keywords(query_keywords)
                examples = [e for e in examples if _matches_keywords(e, keywords)]

            if examples:
                for example in examples[:15]:  # Limit to 15 examples
                    results.append(example)
            else:
                results.append("No matching examples found in this category.")
        else:
            results.append(f"Category `{category}` directory not found.")

    # If no category, search by keywords or list categories
    elif query_keywords:
        keywords = normalize_keywords(query_keywords)

        # Search in all usage directories
        all_matches: list[str] = []
        for cat_name, cat_path in EXAMPLE_CATEGORIES.items():
            cat_dir = base_dir / cat_path
            if cat_dir.exists():
                matched = search_documents(keywords, cat_dir, limit=5)
                for m in matched:
                    all_matches.append(f"- `{cat_path}/{m}` ({cat_name})")

        # Also search snippets
        if snippets_dir.exists():
            snippet_matches = search_documents(keywords, snippets_dir, limit=5)
            for m in snippet_matches:
                all_matches.append(f"- `_snippets/{m}` (snippet)")

        if all_matches:
            results.append("## Matching Examples\n")
            results.append(f"*Keywords: {', '.join(keywords)}*\n")
            results.extend(all_matches[:20])
        else:
            results.append("No examples found matching your keywords.")

    else:
        # List all categories
        results.append("## Available Example Categories\n")
        results.append("Use the `category` parameter to explore examples:\n")

        for cat_name, cat_path in sorted(EXAMPLE_CATEGORIES.items()):
            cat_dir = base_dir / cat_path
            if cat_dir.exists():
                contents = list_directory(cat_dir)
                file_count = len(contents.files) + len(contents.dirs)
                results.append(f"- **{cat_name}** - `{cat_path}/` ({file_count} items)")

        if snippets_dir.exists():
            contents = list_directory(snippets_dir)
            results.append(f"\n**Code Snippets:** {len(contents.files)} reference snippets in `_snippets/`")

    return "\n".join(results)


def _collect_examples_from_dir(dir_path: Path, relative_path: str, depth: int = 0) -> list[str]:
    """Recursively collect example content from a directory."""
    results: list[str] = []

    if depth > 2:  # Limit recursion
        return results

    contents = list_directory(dir_path)

    # Process files first
    for file_name in contents.files[:10]:  # Limit files per directory
        file_path = dir_path / file_name
        frontmatter, content = read_mdx_file(file_path)

        title = frontmatter.get("title", file_name.replace(".mdx", "").replace("-", " ").title())
        file_rel_path = f"{relative_path}/{file_name}"

        # Extract first code block as preview
        code_preview = _extract_code_preview(content)

        example_text = f"\n### {title}\n"
        example_text += f"*File: `{file_rel_path}`*\n"
        if code_preview:
            example_text += f"\n{code_preview}\n"

        results.append(example_text)

    # Process subdirectories
    for dir_name in contents.dirs[:5]:  # Limit subdirs
        subdir_path = dir_path / dir_name.rstrip("/")
        subdir_rel = f"{relative_path}/{dir_name.rstrip('/')}"
        results.extend(_collect_examples_from_dir(subdir_path, subdir_rel, depth + 1))

    return results


def _extract_code_preview(content: str, max_lines: int = 30) -> str:
    """Extract the best Python code block from content as a preview.

    Skips bash/shell code blocks that just create files (touch, mkdir).
    Prefers Python code blocks with actual implementation.
    """
    import re

    # Find all code blocks
    code_blocks = re.findall(r"```(\w+)?[^\n]*\n(.*?)```", content, re.DOTALL)

    if not code_blocks:
        return ""

    # Find the best code block (prefer python with actual code)
    best_block = None
    best_score = -1

    for lang, code in code_blocks:
        lang = (lang or "").lower()
        code_stripped = code.strip()

        # Skip empty blocks
        if not code_stripped:
            continue

        # Skip bash blocks that just create files
        if lang in ("bash", "shell", "sh"):
            if code_stripped.startswith("touch ") or code_stripped.startswith("mkdir "):
                continue
            # Low priority for other bash
            score = 1
        elif lang in ("python", "py"):
            # Check if it has actual code (imports, definitions)
            if "import " in code_stripped or "def " in code_stripped or "class " in code_stripped:
                score = 10
            elif "agent" in code_stripped.lower() or "=" in code_stripped:
                score = 8
            else:
                score = 5
        else:
            score = 2

        if score > best_score:
            best_score = score
            best_block = (lang or "python", code_stripped)

    if not best_block:
        return ""

    lang, code = best_block

    # Truncate if too long
    lines = code.split("\n")
    if len(lines) > max_lines:
        code = "\n".join(lines[:max_lines]) + "\n# ... (truncated)"

    return f"```{lang}\n{code}\n```"


def _matches_keywords(text: str, keywords: list[str]) -> bool:
    """Check if text matches any of the keywords."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def get_examples_description() -> str:
    """Get the tool description."""
    categories = ", ".join(sorted(EXAMPLE_CATEGORIES.keys()))
    return f"""Get code examples and snippets for Agno framework.

Access working code examples demonstrating agents, teams, workflows, tools,
memory, knowledge, and other Agno features.

**Available categories:** {categories}

**Usage:**
- `category="agents"` - Get agent usage examples
- `category="workflows"` - Get workflow pattern examples
- `query_keywords=["streaming", "async"]` - Search for specific examples
- No parameters - List all available categories

Examples include complete, runnable code with proper imports and setup."""
