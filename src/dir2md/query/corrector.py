"""Query Corrector: Auto-correct typos in search queries.

Lightweight typo correction using edit distance without external dependencies.
Improves user experience by fixing common query mistakes.
"""

from typing import Optional, List, Set
import re


class QueryCorrector:
    """Auto-corrects typos in search queries using edit distance.

    Uses a dictionary of common programming terms to suggest corrections.
    """

    # Common programming terms (expandable)
    COMMON_TERMS: Set[str] = {
        # Authentication
        "auth", "authentication", "login", "signin", "session", "token",
        "password", "credential", "oauth", "jwt", "security",

        # Payment
        "payment", "checkout", "billing", "invoice", "transaction",
        "stripe", "paypal", "subscription",

        # Database
        "database", "db", "sql", "query", "schema", "table", "migration",
        "postgres", "mysql", "mongodb", "redis",

        # API
        "api", "endpoint", "route", "controller", "service", "rest",
        "graphql", "http", "request", "response",

        # Testing
        "test", "testing", "spec", "unittest", "pytest", "jest",
        "mock", "fixture", "integration",

        # Config
        "config", "configuration", "settings", "environment", "env",

        # Frontend
        "frontend", "ui", "component", "react", "vue", "angular",
        "dom", "html", "css", "javascript", "typescript",

        # Backend
        "backend", "server", "service", "model", "controller",

        # DevOps
        "docker", "container", "kubernetes", "deployment", "ci", "cd",
        "pipeline", "build", "deploy",

        # Common file types
        "python", "javascript", "typescript", "java", "go", "rust",

        # Common actions
        "create", "read", "update", "delete", "list", "search",
        "validate", "process", "handle", "manage",
    }

    def __init__(self, custom_terms: Optional[Set[str]] = None):
        """Initialize corrector with optional custom terms.

        Args:
            custom_terms: Additional domain-specific terms to recognize
        """
        self.terms = self.COMMON_TERMS.copy()
        if custom_terms:
            self.terms.update(custom_terms)

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein (edit) distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Minimum number of edits needed to transform s1 into s2
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_closest_term(self, word: str, max_distance: int = 2) -> Optional[str]:
        """Find the closest matching term for a given word.

        Args:
            word: Word to correct
            max_distance: Maximum edit distance to consider (default: 2)

        Returns:
            Closest matching term or None if no close match found
        """
        word_lower = word.lower()

        # Exact match (no correction needed)
        if word_lower in self.terms:
            return None

        # Find closest match
        best_match = None
        best_distance = max_distance + 1

        for term in self.terms:
            distance = self._levenshtein_distance(word_lower, term)
            if distance < best_distance:
                best_distance = distance
                best_match = term

        if best_distance <= max_distance:
            return best_match

        return None

    def correct(self, query: str, max_distance: int = 2) -> str:
        """Auto-correct typos in a query.

        Args:
            query: Original query string
            max_distance: Maximum edit distance for corrections

        Returns:
            Corrected query string
        """
        # Split query into words
        words = re.split(r'[\s,|]+', query)
        corrected_words = []

        for word in words:
            word = word.strip()
            if not word:
                continue

            # Try to find correction
            correction = self.find_closest_term(word, max_distance)
            if correction:
                corrected_words.append(correction)
            else:
                corrected_words.append(word)

        # Reconstruct query
        return " ".join(corrected_words)

    def suggest_corrections(self, query: str, max_distance: int = 2) -> List[tuple]:
        """Suggest corrections for each word in query.

        Args:
            query: Original query string
            max_distance: Maximum edit distance for corrections

        Returns:
            List of (original_word, correction) tuples
        """
        words = re.split(r'[\s,|]+', query)
        suggestions = []

        for word in words:
            word = word.strip()
            if not word:
                continue

            correction = self.find_closest_term(word, max_distance)
            if correction and correction != word.lower():
                suggestions.append((word, correction))

        return suggestions


# Example usage
if __name__ == "__main__":
    corrector = QueryCorrector()

    test_queries = [
        "atuh",           # auth
        "payemnt",        # payment
        "databse",        # database
        "konfig",         # config
        "tset",           # test
        "backedn",        # backend
        "deplyo",         # deploy
    ]

    print("Query Typo Correction Examples:\n")

    for query in test_queries:
        corrected = corrector.correct(query)
        if corrected != query:
            print(f"Original:  {query}")
            print(f"Corrected: {corrected}\n")
        else:
            print(f"No correction needed: {query}\n")
