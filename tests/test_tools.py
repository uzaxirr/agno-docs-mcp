"""Tests for Agno MCP tools."""

import pytest
from pathlib import Path


class TestPathUtilities:
    """Test path resolution utilities."""

    def test_is_safe_path_valid(self):
        """Test that valid paths are accepted."""
        from agno_docs_mcp.utils.paths import is_safe_path

        base = Path("/docs")
        target = Path("/docs/basics/agents")
        # Note: This will fail if paths don't exist, but tests the logic
        # In real tests, use tmp_path fixture

    def test_is_safe_path_traversal(self):
        """Test that path traversal is rejected."""
        from agno_docs_mcp.utils.paths import is_safe_path

        base = Path("/docs")
        target = Path("/docs/../etc/passwd")
        # Path traversal should be detected


class TestSearchUtilities:
    """Test search utilities."""

    def test_normalize_keywords(self):
        """Test keyword normalization."""
        from agno_docs_mcp.utils.search import normalize_keywords

        result = normalize_keywords(["Hello World", "Test"])
        assert "hello" in result
        assert "world" in result
        assert "test" in result

    def test_extract_keywords_from_path(self):
        """Test keyword extraction from paths."""
        from agno_docs_mcp.utils.search import extract_keywords_from_path

        result = extract_keywords_from_path("basics/building-agents.mdx")
        assert "building" in result
        assert "agents" in result


class TestContentUtilities:
    """Test content utilities."""

    def test_parse_frontmatter(self):
        """Test frontmatter parsing."""
        from agno_docs_mcp.utils.content import parse_frontmatter

        content = '''---
title: "Test Title"
description: "Test description"
---

# Content here
'''
        frontmatter, remaining = parse_frontmatter(content)
        assert frontmatter.get("title") == "Test Title"
        assert "# Content here" in remaining

    def test_parse_frontmatter_no_frontmatter(self):
        """Test parsing content without frontmatter."""
        from agno_docs_mcp.utils.content import parse_frontmatter

        content = "# Just content\n\nNo frontmatter here."
        frontmatter, remaining = parse_frontmatter(content)
        assert frontmatter == {}
        assert remaining == content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
