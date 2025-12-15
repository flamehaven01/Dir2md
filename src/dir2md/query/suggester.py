"""Query Suggester: Suggest related queries based on file matches.

Analyzes matched files to suggest related search terms, improving
discoverability without requiring user knowledge of codebase structure.
"""

from typing import List, Set, Dict, Counter as CounterType
from collections import Counter
from pathlib import Path
import re


class QuerySuggester:
    """Suggests related queries based on matched files and patterns.

    Analyzes file paths, names, and patterns to recommend related searches.
    """

    # Common file patterns to extract keywords from
    PATTERN_EXTRACTORS = [
        # File names (e.g., auth_service.py -> auth, service)
        r'([a-z]+)_([a-z]+)',
        # Camel case (e.g., AuthService -> auth, service)
        r'([A-Z][a-z]+)',
        # Directory names
        r'/([a-z]+)/',
    ]

    def __init__(self):
        """Initialize suggester."""
        self.query_history: List[str] = []
        self.file_keywords: Dict[str, int] = Counter()

    def extract_keywords_from_path(self, file_path: str) -> Set[str]:
        """Extract keywords from a file path.

        Args:
            file_path: File path to analyze

        Returns:
            Set of extracted keywords
        """
        keywords = set()

        # Extract from file name
        file_name = Path(file_path).stem

        # Split by underscore
        parts = re.split(r'[_\-.]', file_name.lower())
        keywords.update(p for p in parts if len(p) > 2)

        # Split camel case
        camel_parts = re.findall(r'[A-Z][a-z]+', file_name)
        keywords.update(p.lower() for p in camel_parts if len(p) > 2)

        # Extract from directory path
        dir_path = Path(file_path).parent
        dir_parts = [p.lower() for p in dir_path.parts if len(p) > 2]
        keywords.update(dir_parts)

        # Remove common noise words
        noise_words = {'src', 'lib', 'app', 'main', 'core', 'common', 'util', 'test', 'tests', '__pycache__'}
        keywords = keywords - noise_words

        return keywords

    def analyze_matches(self, matched_files: List[str]) -> None:
        """Analyze matched files to update keyword frequencies.

        Args:
            matched_files: List of file paths that matched query
        """
        for file_path in matched_files:
            keywords = self.extract_keywords_from_path(file_path)
            for keyword in keywords:
                self.file_keywords[keyword] += 1

    def suggest_related_queries(
        self,
        current_query: str,
        matched_files: List[str],
        max_suggestions: int = 5
    ) -> List[str]:
        """Suggest related queries based on matched files.

        Args:
            current_query: The current search query
            matched_files: Files that matched the current query
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggested query terms
        """
        # Extract keywords from matched files
        keyword_freq: CounterType[str] = Counter()
        for file_path in matched_files:
            keywords = self.extract_keywords_from_path(file_path)
            for keyword in keywords:
                keyword_freq[keyword] += 1

        # Filter out words already in query
        query_words = set(current_query.lower().split())
        suggestions = [
            keyword for keyword, _ in keyword_freq.most_common(max_suggestions * 2)
            if keyword not in query_words
        ]

        return suggestions[:max_suggestions]

    def suggest_by_directory(self, matched_files: List[str]) -> Dict[str, List[str]]:
        """Group suggestions by directory structure.

        Args:
            matched_files: Files that matched the query

        Returns:
            Dictionary mapping directories to file suggestions
        """
        dir_groups: Dict[str, List[str]] = {}

        for file_path in matched_files:
            dir_name = Path(file_path).parent.name
            if dir_name not in dir_groups:
                dir_groups[dir_name] = []
            dir_groups[dir_name].append(Path(file_path).name)

        return dir_groups

    def add_to_history(self, query: str) -> None:
        """Add a query to search history.

        Args:
            query: Query to add
        """
        if query and query not in self.query_history:
            self.query_history.append(query)

    def get_recent_queries(self, limit: int = 5) -> List[str]:
        """Get recent query history.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of recent queries
        """
        return self.query_history[-limit:]


# Example usage
if __name__ == "__main__":
    suggester = QuerySuggester()

    # Simulate matched files
    matched_files = [
        "src/auth/login_service.py",
        "src/auth/session_manager.py",
        "src/auth/token_validator.py",
        "tests/auth/test_login.py",
        "src/api/auth_controller.py",
    ]

    print("Query Suggestion Examples:\n")

    # Analyze matches
    suggester.analyze_matches(matched_files)

    # Test query
    test_query = "auth"
    suggestions = suggester.suggest_related_queries(test_query, matched_files)

    print(f"Current query: '{test_query}'")
    print(f"Matched {len(matched_files)} files")
    print("\nSuggested related queries:")
    for suggestion in suggestions:
        print(f"  - {suggestion}")

    # Directory grouping
    print("\nFiles grouped by directory:")
    dir_groups = suggester.suggest_by_directory(matched_files)
    for dir_name, files in dir_groups.items():
        print(f"  {dir_name}:")
        for file_name in files:
            print(f"    - {file_name}")
