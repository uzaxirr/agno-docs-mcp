"""Documentation preparation script.

This script copies and organizes documentation from the Agno docs repository
into the .docs/ directory for use by the MCP server.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Any


# Default source directory (can be overridden)
DEFAULT_AGNO_DOCS_PATH = Path("/Users/uzair/Work/agno-docs")


def get_source_docs_path() -> Path:
    """Get the path to the source Agno documentation."""
    import os
    env_path = os.environ.get("AGNO_DOCS_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_AGNO_DOCS_PATH


def get_output_dir() -> Path:
    """Get the output directory for preprocessed docs."""
    return Path(__file__).parent.parent.parent.parent / ".docs"


def copy_docs(source_dir: Path, output_dir: Path) -> dict[str, int]:
    """Copy documentation files from source to output directory.

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

    # Define source directories to copy
    source_mappings = [
        # (source_subdir, dest_subdir)
        ("basics", "basics"),
        ("reference", "reference"),
        ("reference-api", "reference-api"),  # REST API endpoint docs + OpenAPI spec
        ("integrations", "integrations"),
        ("agent-os", "agent-os"),
        ("get-started", "get-started"),
        ("how-to", "how-to"),
        ("faq", "faq"),
        ("examples", "examples"),
    ]

    # Copy each documentation section
    for source_subdir, dest_subdir in source_mappings:
        src_path = source_dir / source_subdir
        dst_path = raw_dir / dest_subdir

        if src_path.exists() and src_path.is_dir():
            copied = copy_directory_recursive(src_path, dst_path)
            stats["docs_copied"] += copied
            stats["directories_created"] += 1
            print(f"  Copied {copied} files from {source_subdir}/")

    # Copy root-level MDX files
    for file in source_dir.glob("*.mdx"):
        shutil.copy2(file, raw_dir / file.name)
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
        help="Path to Agno docs directory (default: from AGNO_DOCS_PATH env or /Users/uzair/Work/agno-docs)"
    )
    args = parser.parse_args()

    prepare_docs(args.source)


if __name__ == "__main__":
    main()
