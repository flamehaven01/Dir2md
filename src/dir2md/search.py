from __future__ import annotations

"""Lightweight query matching utilities for dir2md."""

import textwrap


def match_query_snippet(content: str, query: str, window: int = 160, width: int = 300) -> tuple[int, str]:
    """Return a simple match score and surrounding snippet for a query string."""
    if not content or not query:
        return 0, ""

    haystack = content.lower()
    needle = query.lower()
    idx = haystack.find(needle)
    if idx == -1:
        return 0, ""

    # Score: count of case-insensitive occurrences
    score = haystack.count(needle)

    start = max(idx - window, 0)
    end = min(idx + len(needle) + window, len(content))
    snippet = content[start:end].replace("\n", " ").strip()
    snippet = " ".join(snippet.split())
    snippet = textwrap.shorten(snippet, width=width, placeholder="...")
    return score, snippet
