"""Documentation preparation script.

This script copies and organizes documentation from the Agno docs repository
into the .docs/ directory for use by the MCP server.

The agno-docs repo has a flat structure (agents/, teams/, memory/, etc.)
but the MCP tools expect a reorganized layout:
  - basics/    → core concept docs (agents, teams, workflows, tools, memory, etc.)
  - reference/ → SDK class/method reference
  - integrations/ → database providers, vector stores, model providers, toolkits
  - agent-os/  → AgentOS runtime docs
  - how-to/    → migration guides, install, contributing (from other/)
  - faq/       → FAQ docs
  - examples/  → cookbook examples

This script handles the mapping from the real repo structure to what tools expect.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Any


# Default: look for agno-docs as a sibling or subdirectory
def _find_default_agno_docs_path() -> Path:
    """Try to auto-detect the agno-docs location."""
    project_root = Path(__file__).parent.parent.parent.parent
    # Check if agno-docs is a subdirectory of the project
    candidate = project_root / "agno-docs"
    if candidate.exists():
        return candidate
    # Fallback: sibling directory
    candidate = project_root.parent / "agno-docs"
    if candidate.exists():
        return candidate
    # Last resort: return the subdirectory path (will fail with helpful error)
    return project_root / "agno-docs"


def get_source_docs_path() -> Path:
    """Get the path to the source Agno documentation."""
    import os
    env_path = os.environ.get("AGNO_DOCS_PATH")
    if env_path:
        return Path(env_path)
    return _find_default_agno_docs_path()


def get_output_dir() -> Path:
    """Get the output directory for preprocessed docs."""
    return Path(__file__).parent.parent.parent.parent / ".docs"


def copy_docs(source_dir: Path, output_dir: Path) -> dict[str, int]:
    """Copy documentation files from source to output directory.

    Reorganizes the flat agno-docs repo structure into the layout
    expected by the MCP tools.

    Args:
        source_dir: Source Agno docs directory
        output_dir: Output .docs directory

    Returns:
        Dictionary with copy statistics
    """
    raw_dir = output_dir / "raw"
    snippets_dir = output_dir / "snippets"

    # Clean and recreate directories
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    if snippets_dir.exists():
        shutil.rmtree(snippets_dir)

    raw_dir.mkdir(parents=True, exist_ok=True)
    snippets_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "docs_copied": 0,
        "snippets_copied": 0,
        "directories_created": 0,
    }

    # ─── 1. "basics/" — Core SDK concept docs ───
    # The tools expect basics/agents/, basics/teams/, etc.
    # In the real repo these are top-level directories.
    basics_sources = [
        "agents", "teams", "workflows", "tools", "memory", "knowledge",
        "models", "database", "evals", "guardrails", "hitl", "multimodal",
        "reasoning", "sessions", "tracing", "compression", "context",
        "hooks", "skills", "state", "templates", "history",
        "input-output", "run-cancellation", "learning",
    ]
    for subdir in basics_sources:
        src_path = source_dir / subdir
        dst_path = raw_dir / "basics" / subdir
        if src_path.exists() and src_path.is_dir():
            copied = copy_directory_recursive(src_path, dst_path)
            stats["docs_copied"] += copied
            stats["directories_created"] += 1
            print(f"  Copied {copied} files from {subdir}/ → basics/{subdir}/")

    # ─── 2. Direct-copy directories (already match expected layout) ───
    direct_mappings = [
        ("reference", "reference"),
        ("reference-api", "reference-api"),
        ("agent-os", "agent-os"),
        ("faq", "faq"),
        ("integrations", "integrations"),  # base integrations dir (discord, memory, testing)
        ("production", "production"),
        ("dependencies", "dependencies"),
        ("cookbook", "examples"),  # cookbook → examples
    ]
    for source_subdir, dest_subdir in direct_mappings:
        src_path = source_dir / source_subdir
        dst_path = raw_dir / dest_subdir
        if src_path.exists() and src_path.is_dir():
            copied = copy_directory_recursive(src_path, dst_path)
            stats["docs_copied"] += copied
            stats["directories_created"] += 1
            print(f"  Copied {copied} files from {source_subdir}/ → {dest_subdir}/")

    # ─── 3. "how-to/" — Migration guides (from other/) ───
    other_src = source_dir / "other"
    howto_dst = raw_dir / "how-to"
    if other_src.exists() and other_src.is_dir():
        copied = copy_directory_recursive(other_src, howto_dst)
        stats["docs_copied"] += copied
        stats["directories_created"] += 1
        print(f"  Copied {copied} files from other/ → how-to/")

    # ─── 4. "integrations/" — Provider docs from various sources ───
    # database providers → integrations/database/
    db_providers_src = source_dir / "database" / "providers"
    db_providers_dst = raw_dir / "integrations" / "database"
    if db_providers_src.exists():
        copied = copy_directory_recursive(db_providers_src, db_providers_dst)
        stats["docs_copied"] += copied
        print(f"  Copied {copied} files from database/providers/ → integrations/database/")

    # vector store providers → integrations/vectordb/
    vs_src = source_dir / "knowledge" / "vector-stores"
    vs_dst = raw_dir / "integrations" / "vectordb"
    if vs_src.exists():
        copied = copy_directory_recursive(vs_src, vs_dst)
        stats["docs_copied"] += copied
        print(f"  Copied {copied} files from knowledge/vector-stores/ → integrations/vectordb/")

    # model providers → integrations/models/
    models_src = source_dir / "models" / "providers"
    models_dst = raw_dir / "integrations" / "models"
    if models_src.exists():
        copied = copy_directory_recursive(models_src, models_dst)
        stats["docs_copied"] += copied
        print(f"  Copied {copied} files from models/providers/ → integrations/models/")

    # toolkits → integrations/toolkits/
    toolkits_src = source_dir / "tools" / "toolkits"
    toolkits_dst = raw_dir / "integrations" / "toolkits"
    if toolkits_src.exists():
        copied = copy_directory_recursive(toolkits_src, toolkits_dst)
        stats["docs_copied"] += copied
        print(f"  Copied {copied} files from tools/toolkits/ → integrations/toolkits/")

    # observability → integrations/observability/
    obs_src = source_dir / "observability"
    obs_dst = raw_dir / "integrations" / "observability"
    if obs_src.exists():
        copied = copy_directory_recursive(obs_src, obs_dst)
        stats["docs_copied"] += copied
        print(f"  Copied {copied} files from observability/ → integrations/observability/")

    # ─── 5. Copy each documentation section (legacy mappings, skip if already copied) ───
    # This is a no-op safety net for any directories not covered above
    legacy_mappings = [
        ("get-started", "get-started"),
        ("how-to", "how-to"),
        ("basics", "basics"),
        ("examples", "examples"),
    ]
    for source_subdir, dest_subdir in legacy_mappings:
        src_path = source_dir / source_subdir
        dst_path = raw_dir / dest_subdir
        if src_path.exists() and src_path.is_dir() and not dst_path.exists():
            copied = copy_directory_recursive(src_path, dst_path)
            stats["docs_copied"] += copied
            stats["directories_created"] += 1
            print(f"  Copied {copied} files from {source_subdir}/")

    # ─── 6. Root-level MDX files → raw/ and get-started/ ───
    get_started_dir = raw_dir / "get-started"
    get_started_dir.mkdir(parents=True, exist_ok=True)

    for file in source_dir.glob("*.mdx"):
        shutil.copy2(file, raw_dir / file.name)
        # Also copy intro/getting-started files to get-started/
        if file.stem in ("introduction", "first-agent", "first-multi-agent-system",
                         "index", "get-help", "performance"):
            shutil.copy2(file, get_started_dir / file.name)
        stats["docs_copied"] += 1

    for file in source_dir.glob("*.md"):
        if file.name != "README.md":
            shutil.copy2(file, raw_dir / file.name)
            stats["docs_copied"] += 1

    # Copy snippets
    snippets_src = source_dir / "_snippets"
    if snippets_src.exists():
        copied = copy_directory_recursive(snippets_src, snippets_dir)
        stats["snippets_copied"] = copied
        print(f"  Copied {copied} snippet files")

    # Copy OpenAPI spec file for REST API documentation
    openapi_src = source_dir / "reference-api" / "openapi.json"
    if openapi_src.exists():
        shutil.copy2(openapi_src, output_dir / "openapi.json")
        print(f"  Copied OpenAPI spec (openapi.json)")

    return stats


def copy_directory_recursive(src: Path, dst: Path) -> int:
    """Recursively copy a directory, keeping only MDX/MD files.

    Args:
        src: Source directory
        dst: Destination directory

    Returns:
        Number of files copied
    """
    dst.mkdir(parents=True, exist_ok=True)
    count = 0

    for item in src.iterdir():
        if item.is_dir():
            count += copy_directory_recursive(item, dst / item.name)
        elif item.is_file() and item.suffix in (".mdx", ".md"):
            shutil.copy2(item, dst / item.name)
            count += 1

    return count


def build_index(output_dir: Path) -> dict[str, Any]:
    """Build a search index of all documentation files.

    Args:
        output_dir: The .docs output directory

    Returns:
        Index dictionary
    """
    raw_dir = output_dir / "raw"
    index: dict[str, Any] = {
        "version": "1.0",
        "files": [],
        "categories": {},
    }

    if not raw_dir.exists():
        return index

    for file_path in raw_dir.rglob("*.mdx"):
        relative_path = str(file_path.relative_to(raw_dir)).replace("\\", "/")
        category = relative_path.split("/")[0] if "/" in relative_path else "root"

        # Extract title from frontmatter
        title = extract_title(file_path)

        file_entry = {
            "path": relative_path,
            "title": title,
            "category": category,
        }
        index["files"].append(file_entry)

        # Update category count
        if category not in index["categories"]:
            index["categories"][category] = 0
        index["categories"][category] += 1

    for file_path in raw_dir.rglob("*.md"):
        relative_path = str(file_path.relative_to(raw_dir)).replace("\\", "/")
        category = relative_path.split("/")[0] if "/" in relative_path else "root"

        title = extract_title(file_path)

        file_entry = {
            "path": relative_path,
            "title": title,
            "category": category,
        }
        index["files"].append(file_entry)

        if category not in index["categories"]:
            index["categories"][category] = 0
        index["categories"][category] += 1

    # Save index
    index_path = output_dir / "index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    return index


def extract_title(file_path: Path) -> str:
    """Extract title from a documentation file's frontmatter.

    Args:
        file_path: Path to the MDX/MD file

    Returns:
        Title string or filename as fallback
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            import re
            end_match = re.search(r"\n---\s*\n", content[3:])
            if end_match:
                frontmatter = content[3:end_match.start() + 3]
                title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
                if title_match:
                    return title_match.group(1).strip('"\'')
    except Exception:
        pass

    return file_path.stem.replace("-", " ").title()


def prepare_docs(source_path: Path | None = None) -> None:
    """Main function to prepare documentation.

    Args:
        source_path: Optional source path override
    """
    source_dir = source_path or get_source_docs_path()
    output_dir = get_output_dir()

    print(f"Preparing Agno documentation...")
    print(f"  Source: {source_dir}")
    print(f"  Output: {output_dir}")
    print()

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("Set AGNO_DOCS_PATH environment variable or edit DEFAULT_AGNO_DOCS_PATH")
        sys.exit(1)

    # Copy documentation
    print("Copying documentation files...")
    stats = copy_docs(source_dir, output_dir)
    print()

    # Build index
    print("Building search index...")
    index = build_index(output_dir)
    print(f"  Indexed {len(index['files'])} files in {len(index['categories'])} categories")
    print()

    # Summary
    print("Done!")
    print(f"  Total docs copied: {stats['docs_copied']}")
    print(f"  Snippets copied: {stats['snippets_copied']}")
    print(f"  Categories: {', '.join(index['categories'].keys())}")


def main() -> None:
    """CLI entry point for prepare_docs."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Prepare Agno documentation for the MCP server"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to Agno docs directory (default: auto-detect from AGNO_DOCS_PATH env or ./agno-docs)"
    )
    args = parser.parse_args()

    prepare_docs(args.source)


if __name__ == "__main__":
    main()
