"""Keyword-based search utilities for documentation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


@dataclass
class FileScore:
    """Score for a file based on keyword matching."""
    path: str
    keyword_matches: set[str] = field(default_factory=set)
    total_matches: int = 0
    title_matches: int = 0
    path_relevance: int = 0


# Cache for MDX file paths per directory
_mdx_file_cache: dict[str, list[str]] = {}


def walk_mdx_files(base_dir: Path) -> Iterator[Path]:
    """Walk through all MDX files in a directory recursively.

    Uses caching to avoid repeated filesystem scans.

    Args:
        base_dir: Base directory to scan

    Yields:
        Path objects for each MDX file found
    """
    cache_key = str(base_dir)

    if cache_key in _mdx_file_cache:
        for file_path in _mdx_file_cache[cache_key]:
            yield Path(file_path)
        return

    files_found: list[str] = []

    def _scan_dir(dir_path: Path) -> None:
        try:
            for entry in dir_path.iterdir():
                if entry.is_dir():
                    _scan_dir(entry)
                elif entry.is_file() and entry.suffix in (".mdx", ".md"):
                    files_found.append(str(entry))
        except PermissionError:
            pass

    _scan_dir(base_dir)
    _mdx_file_cache[cache_key] = files_found

    for file_path in files_found:
        yield Path(file_path)


def calculate_path_relevance(file_path: str, keywords: list[str]) -> int:
    """Calculate relevance score based on file path.

    Args:
        file_path: Relative path to the file
        keywords: List of search keywords

    Returns:
        Relevance score (higher is better)
    """
    relevance = 0
    path_lower = file_path.lower()

    # Boost for reference docs
    if path_lower.startswith("reference/"):
        relevance += 2

    # Boost if path contains any keywords
    for keyword in keywords:
        if keyword.lower() in path_lower:
            relevance += 3

    # Boost for high-value directories (Agno-specific)
    high_value_dirs = [
        "agents", "teams", "workflows", "tools", "memory",
        "knowledge", "models", "agentos", "integrations"
    ]
    if any(d in path_lower for d in high_value_dirs):
        relevance += 1

    return relevance


def calculate_final_score(score: FileScore, total_keywords: int) -> int:
    """Calculate the final ranking score for a file.

    Args:
        score: FileScore object with match data
        total_keywords: Total number of keywords in the search

    Returns:
        Final score for ranking
    """
    # Bonus if all keywords were found
    all_keywords_bonus = 10 if len(score.keyword_matches) == total_keywords else 0

    return (
        score.total_matches * 1 +
        score.title_matches * 3 +
        score.path_relevance * 2 +
        len(score.keyword_matches) * 5 +
        all_keywords_bonus
    )


def search_documents(
    keywords: list[str],
    base_dir: Path,
    limit: int = 10
) -> list[str]:
    """Search documents by keywords.

    Args:
        keywords: List of search keywords
        base_dir: Base directory to search in
        limit: Maximum number of results to return

    Returns:
        List of relative file paths, ranked by relevance
    """
    if not keywords:
        return []

    file_scores: dict[str, FileScore] = {}

    for file_path in walk_mdx_files(base_dir):
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        relative_path = str(file_path.relative_to(base_dir)).replace("\\", "/")

        for line in content.split("\n"):
            line_lower = line.lower()

            for keyword in keywords:
                if keyword.lower() in line_lower:
                    if relative_path not in file_scores:
                        file_scores[relative_path] = FileScore(
                            path=relative_path,
                            path_relevance=calculate_path_relevance(relative_path, keywords)
                        )

                    score = file_scores[relative_path]
                    score.keyword_matches.add(keyword)
                    score.total_matches += 1

                    # Check if this is a title/heading line
                    if line.startswith("#") or "title" in line_lower:
                        score.title_matches += 1

    # Sort by final score
    ranked_files = sorted(
        file_scores.values(),
        key=lambda s: calculate_final_score(s, len(keywords)),
        reverse=True
    )

    return [f.path for f in ranked_files[:limit]]


def extract_keywords_from_path(path: str) -> list[str]:
    """Extract keywords from a file path.

    Args:
        path: File path to extract keywords from

    Returns:
        List of keywords extracted from the path
    """
    import re

    # Get only the filename (last part of the path)
    filename = path.split("/")[-1]
    filename = re.sub(r"\.(mdx|md)$", "", filename)

    keywords: set[str] = set()

    # Split on hyphens, underscores, and camelCase
    parts = re.split(r"[-_]|(?=[A-Z])", filename)

    for part in parts:
        part = part.lower().strip()
        if len(part) > 2:
            keywords.add(part)

    return list(keywords)


def normalize_keywords(keywords: list[str]) -> list[str]:
    """Normalize a list of keywords.

    Splits multi-word keywords, lowercases, and deduplicates.

    Args:
        keywords: Raw list of keywords

    Returns:
        Normalized list of unique keywords
    """
    normalized: set[str] = set()

    for keyword in keywords:
        # Split on whitespace
        for part in keyword.split():
            part = part.lower().strip()
            if part:
                normalized.add(part)

    return list(normalized)


def get_matching_paths(
    doc_path: str,
    query_keywords: list[str] | None,
    base_dir: Path
) -> str:
    """Get suggested paths based on keywords.

    Combines keywords from the path and query to find relevant documents.

    Args:
        doc_path: The documentation path (may be non-existent)
        query_keywords: Keywords from the user's query
        base_dir: Base directory for documentation

    Returns:
        Formatted string with suggested paths
    """
    path_keywords = extract_keywords_from_path(doc_path)
    all_keywords = normalize_keywords(path_keywords + (query_keywords or []))

    if not all_keywords:
        return ""

    suggested_paths = search_documents(all_keywords, base_dir)

    if not suggested_paths:
        return ""

    path_list = "\n".join(f"- `{p}`" for p in suggested_paths)
    return f"**Suggested paths based on your query:**\n\n{path_list}"


def calculate_relevance_score(content: str, keywords: list[str]) -> int:
    """Calculate a simple relevance score for content.

    Args:
        content: Text content to score
        keywords: Keywords to match

    Returns:
        Relevance score
    """
    if not keywords:
        return 0

    score = 0
    content_lower = content.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Count occurrences
        count = content_lower.count(keyword_lower)
        score += count

    return score
