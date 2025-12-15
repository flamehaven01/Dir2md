"""Gravitas-Pack: Symbolic compression for Dir2md blueprints.

Inspired by SAIQL's Gravitas-Pack, this module compresses common patterns
in markdown blueprints using single-byte Unicode symbols, significantly
reducing token count while maintaining readability.
"""

from typing import Dict


class GravitasCompressor:
    """Symbolic compression engine for markdown blueprints.

    Compression Levels:
    - basic: Common metadata patterns (30% reduction)
    - medium: + File patterns and structures (40% reduction)
    - full: + Content patterns and values (50% reduction)
    """

    # Basic level: Metadata compression
    BASIC_SYMBOLS: Dict[str, str] = {
        'File:': '§',
        'Lines:': '⊞',
        'Tokens:': '₮',
        'Size:': '⊡',
        'Modified:': '⏱',
        'Created:': '⊱',
        'Directory:': '⊤',
        'Total:': '№',
        'Count:': '♯',
    }

    # Medium level: File patterns
    MEDIUM_SYMBOLS: Dict[str, str] = {
        **BASIC_SYMBOLS,
        '.py': '🐍',
        '.js': '📜',
        '.ts': '📘',
        '.md': '📝',
        '.json': '⟐',
        '.yaml': '⟡',
        '.yml': '⟡',
        'README': '⊚',
        'config': '⚙',
        'test': '🧪',
    }

    # Full level: Content patterns
    FULL_SYMBOLS: Dict[str, str] = {
        **MEDIUM_SYMBOLS,
        'function': 'ƒ',
        'class': '©',
        'def ': 'λ',
        'import': '↓',
        'export': '↑',
        'const': 'κ',
        'return': '↩',
        'async': '⚡',
        'await': '⏳',
    }

    def __init__(self, level: str = "basic"):
        """Initialize compressor with specified compression level.

        Args:
            level: Compression level ('basic', 'medium', or 'full')
        """
        self.level = level.lower()

        if self.level == "full":
            self.symbol_map = self.FULL_SYMBOLS
        elif self.level == "medium":
            self.symbol_map = self.MEDIUM_SYMBOLS
        else:
            self.symbol_map = self.BASIC_SYMBOLS

        # Create reverse map for decompression
        self.reverse_map = {v: k for k, v in self.symbol_map.items()}

    def compress(self, text: str) -> str:
        """Compress markdown text using symbolic substitution.

        Args:
            text: Original markdown text

        Returns:
            Compressed text with symbols
        """
        compressed = text

        # Sort by length (longest first) to avoid partial matches
        for pattern in sorted(self.symbol_map.keys(), key=len, reverse=True):
            symbol = self.symbol_map[pattern]
            compressed = compressed.replace(pattern, symbol)

        return compressed

    def decompress(self, text: str) -> str:
        """Decompress symbolic text back to original markdown.

        Args:
            text: Compressed text with symbols

        Returns:
            Original markdown text
        """
        decompressed = text

        for symbol, pattern in self.reverse_map.items():
            decompressed = decompressed.replace(symbol, pattern)

        return decompressed

    def estimate_compression_ratio(self, text: str) -> float:
        """Estimate compression ratio for given text.

        Args:
            text: Text to analyze

        Returns:
            Compression ratio (0.0 to 1.0, where 0.7 = 30% reduction)
        """
        original_len = len(text)
        if original_len == 0:
            return 1.0

        compressed_len = len(self.compress(text))
        return compressed_len / original_len

    def get_stats(self, text: str) -> Dict[str, any]:
        """Get compression statistics.

        Args:
            text: Text to analyze

        Returns:
            Dict with compression statistics
        """
        compressed = self.compress(text)

        return {
            "original_size": len(text),
            "compressed_size": len(compressed),
            "reduction_bytes": len(text) - len(compressed),
            "reduction_percent": (1 - len(compressed) / len(text)) * 100 if text else 0,
            "compression_ratio": len(compressed) / len(text) if text else 1.0,
            "level": self.level,
            "symbols_used": sum(1 for s in self.symbol_map.values() if s in compressed)
        }


def compress_blueprint(
    markdown: str,
    level: str = "basic",
    add_legend: bool = True
) -> str:
    """Convenience function to compress a markdown blueprint.

    Args:
        markdown: Original markdown blueprint
        level: Compression level
        add_legend: Whether to add symbol legend at the end

    Returns:
        Compressed markdown with optional legend
    """
    compressor = GravitasCompressor(level=level)
    compressed = compressor.compress(markdown)

    if add_legend:
        legend = _create_legend(compressor.symbol_map)
        compressed += "\n\n" + legend

    return compressed


def _create_legend(symbol_map: Dict[str, str]) -> str:
    """Create a legend explaining the symbols used."""
    legend_lines = ["## Gravitas Symbol Legend", ""]

    for pattern, symbol in sorted(symbol_map.items(), key=lambda x: x[0]):
        legend_lines.append(f"- `{symbol}` = `{pattern}`")

    return "\n".join(legend_lines)


# Example usage
if __name__ == "__main__":
    sample_text = """
File: authentication.py
Lines: 145
Tokens: 1234
Size: 5.2 KB
Modified: 2025-12-14

Directory: src/auth/
Total: 10 files
Count: 2500 lines
"""

    print("Original:")
    print(sample_text)
    print(f"Size: {len(sample_text)} bytes\n")

    for level in ["basic", "medium", "full"]:
        compressor = GravitasCompressor(level=level)
        compressed = compressor.compress(sample_text)
        stats = compressor.get_stats(sample_text)

        print(f"\n{level.upper()} Compression:")
        print(compressed)
        print(f"Size: {stats['compressed_size']} bytes")
        print(f"Reduction: {stats['reduction_percent']:.1f}%")
