"""Semantic Sampler: AST-based intelligent code sampling.

Extracts high-value code sections (classes, functions, docstrings) while
reducing low-value implementation details. Reduces tokens while preserving
semantic understanding.
"""

import ast
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class NodePriority(Enum):
    """Priority levels for AST nodes."""
    CRITICAL = 4  # Public classes, main functions
    HIGH = 3      # Public functions, class methods
    MEDIUM = 2    # Private functions, important variables
    LOW = 1       # Implementation details


@dataclass
class CodeSegment:
    """Represents an extracted code segment with priority."""
    node_type: str
    name: str
    lineno: int
    end_lineno: int
    priority: NodePriority
    docstring: Optional[str]
    signature: str
    content: str


class SemanticSampler:
    """Samples Python code intelligently using AST analysis.

    Extracts structure and signatures while reducing implementation details.
    """

    def __init__(self, preserve_ratio: float = 0.6):
        """Initialize semantic sampler.

        Args:
            preserve_ratio: Ratio of content to preserve (0.0-1.0)
                           0.6 = preserve 60%, remove 40% of low-priority content
        """
        self.preserve_ratio = max(0.1, min(1.0, preserve_ratio))

    def _get_node_priority(self, node: ast.AST, name: str) -> NodePriority:
        """Determine priority of an AST node.

        Args:
            node: AST node
            name: Name of the node

        Returns:
            NodePriority enum value
        """
        # Public classes are critical
        if isinstance(node, ast.ClassDef) and not name.startswith('_'):
            return NodePriority.CRITICAL

        # Main/entry functions are critical
        if isinstance(node, ast.FunctionDef):
            if name in ['main', '__main__', 'run', 'execute']:
                return NodePriority.CRITICAL
            # Public functions are high priority
            if not name.startswith('_'):
                return NodePriority.HIGH
            # Private functions are medium
            return NodePriority.MEDIUM

        # Variables and other nodes
        return NodePriority.LOW

    def _extract_signature(self, node: ast.AST) -> str:
        """Extract function/class signature.

        Args:
            node: AST node (ClassDef or FunctionDef)

        Returns:
            Signature string
        """
        if isinstance(node, ast.ClassDef):
            # Class signature with bases
            bases = ", ".join(ast.unparse(base) for base in node.bases) if node.bases else ""
            if bases:
                return f"class {node.name}({bases})"
            return f"class {node.name}"

        elif isinstance(node, ast.FunctionDef):
            # Function signature with args
            args = ast.unparse(node.args) if node.args else ""
            returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
            decorators = "".join(f"@{ast.unparse(d)}\n" for d in node.decorator_list)
            return f"{decorators}def {node.name}({args}){returns}"

        return str(node)

    def _extract_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from node.

        Args:
            node: AST node

        Returns:
            Docstring text or None
        """
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.Module)):
            docstring = ast.get_docstring(node)
            return docstring

        return None

    def analyze_python_file(self, source_code: str) -> List[CodeSegment]:
        """Analyze Python source code and extract semantic segments.

        Args:
            source_code: Python source code string

        Returns:
            List of CodeSegment objects sorted by priority
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Return empty list if code can't be parsed
            return []

        segments = []

        # Extract module docstring
        module_doc = ast.get_docstring(tree)
        if module_doc:
            segments.append(CodeSegment(
                node_type="module",
                name="__doc__",
                lineno=1,
                end_lineno=1,
                priority=NodePriority.HIGH,
                docstring=module_doc,
                signature="# Module Documentation",
                content=module_doc
            ))

        # Walk through AST nodes
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                name = node.name
                priority = self._get_node_priority(node, name)
                signature = self._extract_signature(node)
                docstring = self._extract_docstring(node)

                # Get source lines
                lineno = node.lineno
                end_lineno = node.end_lineno or lineno

                segments.append(CodeSegment(
                    node_type="class" if isinstance(node, ast.ClassDef) else "function",
                    name=name,
                    lineno=lineno,
                    end_lineno=end_lineno,
                    priority=priority,
                    docstring=docstring,
                    signature=signature,
                    content=""  # Will be filled later if needed
                ))

        # Sort by priority (high to low) then by line number
        segments.sort(key=lambda s: (-s.priority.value, s.lineno))

        return segments

    def sample_python_code(
        self,
        source_code: str,
        max_lines: Optional[int] = None
    ) -> Tuple[str, Dict[str, any]]:
        """Sample Python code intelligently, preserving structure.

        Args:
            source_code: Original Python source code
            max_lines: Maximum lines to keep (None = use preserve_ratio)

        Returns:
            Tuple of (sampled_code, stats_dict)
        """
        lines = source_code.splitlines(keepends=True)
        total_lines = len(lines)

        # Analyze code structure
        segments = self.analyze_python_file(source_code)

        if not segments:
            # Fallback: no AST analysis, return original
            return source_code, {
                "method": "fallback",
                "original_lines": total_lines,
                "sampled_lines": total_lines,
                "reduction": 0,
            }

        # Calculate target lines
        if max_lines is None:
            target_lines = int(total_lines * self.preserve_ratio)
        else:
            target_lines = min(max_lines, total_lines)

        # Build sampled content
        sampled_parts = []
        included_lines = 0

        # Include high-priority segments first
        for segment in segments:
            if included_lines >= target_lines:
                break

            # Always include signature and docstring
            sampled_parts.append(f"\n# {segment.node_type.upper()}: {segment.name} (line {segment.lineno})\n")
            sampled_parts.append(segment.signature)

            if segment.docstring:
                sampled_parts.append(f'\n    """{segment.docstring}"""')

            # For critical/high priority, include partial implementation
            if segment.priority in [NodePriority.CRITICAL, NodePriority.HIGH]:
                sampled_parts.append("\n    ... # (implementation details)")

            sampled_parts.append("\n")
            included_lines += 5  # Rough estimate

        sampled_code = "".join(sampled_parts)
        sampled_lines = len(sampled_code.splitlines())

        stats = {
            "method": "ast_semantic",
            "original_lines": total_lines,
            "sampled_lines": sampled_lines,
            "reduction": ((total_lines - sampled_lines) / total_lines * 100) if total_lines > 0 else 0,
            "segments_extracted": len(segments),
            "critical_count": sum(1 for s in segments if s.priority == NodePriority.CRITICAL),
            "high_count": sum(1 for s in segments if s.priority == NodePriority.HIGH),
        }

        return sampled_code, stats

    def should_use_semantic_sampling(self, file_path: str, file_size: int) -> bool:
        """Determine if semantic sampling should be used for a file.

        Args:
            file_path: Path to the file
            file_size: Size of file in bytes

        Returns:
            True if semantic sampling is beneficial
        """
        # Only for Python files
        if not file_path.endswith('.py'):
            return False

        # Only for files larger than 500 bytes (avoid overhead for tiny files)
        if file_size < 500:
            return False

        return True


# Example usage
if __name__ == "__main__":
    sampler = SemanticSampler(preserve_ratio=0.5)

    # Sample Python code
    sample_code = '''
"""Example module for testing semantic sampling."""

import os
import sys

class DataProcessor:
    """Processes data with various transformations."""

    def __init__(self, config):
        """Initialize processor with config.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._cache = {}

    def process(self, data):
        """Process the input data.

        Args:
            data: Input data to process

        Returns:
            Processed result
        """
        result = self._transform(data)
        result = self._validate(result)
        return result

    def _transform(self, data):
        """Internal transformation logic."""
        # Complex implementation details here
        transformed = data.upper()
        transformed = transformed.strip()
        return transformed

    def _validate(self, data):
        """Internal validation logic."""
        if not data:
            raise ValueError("Empty data")
        return data


def main():
    """Main entry point."""
    processor = DataProcessor({"mode": "production"})
    result = processor.process("hello world")
    print(result)


if __name__ == "__main__":
    main()
'''

    print("AST Semantic Sampling Example:\n")
    print("=" * 60)
    print("ORIGINAL CODE:")
    print("=" * 60)
    print(sample_code)
    print()

    sampled, stats = sampler.sample_python_code(sample_code)

    print("=" * 60)
    print("SAMPLED CODE (50% target):")
    print("=" * 60)
    print(sampled)
    print()

    print("=" * 60)
    print("STATISTICS:")
    print("=" * 60)
    for key, value in stats.items():
        print(f"  {key}: {value}")
