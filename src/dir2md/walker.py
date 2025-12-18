"""Filesystem walking and include/exclude handling."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, List

try:
    from pathspec import PathSpec
except Exception:
    PathSpec = None  # type: ignore

from .gitignore import build_gitignore_matcher


_GLOB_SPECIAL_CHARS = set("*?[")


def _expand_glob_patterns(patterns: List[str]) -> list[str]:
    """
    Normalize glob patterns without aggressive auto-expansion.

    Respects user intent per gitignore standard:
    - foo/     means foo/ in current context
    - **/foo   means recursive search
    - foo/**   means everything under foo/

    Removed in v1.2.1: Automatic expansion of non-glob patterns.
    Reason: Violated principle of least surprise, caused performance issues in large repos.
    """
    expanded: list[str] = []
    seen: set[str] = set()
    for raw in patterns:
        if not raw:
            continue
        normalized = raw.replace("\\", "/")
        if not normalized:
            continue
        # Respect user intent - no automatic expansion
        if normalized not in seen:
            seen.add(normalized)
            expanded.append(normalized)
    return expanded


def _pattern_allows_root_file(pattern: str) -> bool:
    normalized = pattern.lstrip("/")
    if not normalized:
        return True
    consumed_recursive = False
    while normalized.startswith("**/"):
        consumed_recursive = True
        normalized = normalized[3:]
    if not normalized:
        return False
    if "/" not in normalized:
        if consumed_recursive and "*" in normalized:
            return False
        return True
    return False


def _compile_pathspec(patterns: List[str]):
    expanded = _expand_glob_patterns(patterns)
    if not expanded:
        return None
    spec = PathSpec.from_lines("gitwildmatch", expanded)
    allows_root = any(_pattern_allows_root_file(p) for p in expanded)
    return type("Compiled", (), {"spec": spec, "allows_root_files": allows_root})


def _matches_spec(spec, root: Path, path: Path) -> bool:
    if spec is None:
        return False
    try:
        relative_path = str(path.relative_to(root)).replace("\\", "/")
    except ValueError:
        return False
    matched = spec.spec.match_file(relative_path)
    if not matched:
        return False
    if "/" not in relative_path and not spec.allows_root_files:
        return False
    return True


def collect_files(
    root: Path,
    include_globs: List[str],
    exclude_globs: List[str],
    omit_globs: List[str],
    respect_gitignore: bool,
    follow_symlinks: bool,
    stats,
) -> tuple[List[Path], List[str], Callable[[Path], bool], Callable[[Path], bool]]:
    """Walk the tree and return (files, tree_lines, is_included, is_omitted)."""
    gitignore = build_gitignore_matcher(root) if respect_gitignore else None
    include_spec = _compile_pathspec(include_globs)
    exclude_spec = _compile_pathspec(exclude_globs)
    omit_spec = _compile_pathspec(omit_globs)

    def is_ignored(p: Path) -> bool:
        if gitignore and gitignore(str(p.relative_to(root) if p != root else "")):
            return True
        return _matches_spec(exclude_spec, root, p)

    def is_omitted(p: Path) -> bool:
        return _matches_spec(omit_spec, root, p)

    def is_included(p: Path) -> bool:
        if include_spec is None:
            return True
        return _matches_spec(include_spec, root, p)

    tree_lines: list[str] = [str(root)]
    files: list[Path] = []

    def walk(current: Path, prefix: str = "") -> None:
        stats.total_dirs += 1
        try:
            entries = sorted(list(current.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            return
        entries = [e for e in entries if not is_ignored(e)]
        for i, child in enumerate(entries):
            last = i == len(entries) - 1
            joint = "`-- " if last else "|-- "
            tree_lines.append(f"{prefix}{joint}{child.name}")
            if child.is_dir():
                if child.is_symlink() and not follow_symlinks:
                    continue
                walk(child, prefix + ("    " if last else "|   "))
            else:
                files.append(child)

    walk(root)
    return files, tree_lines, is_included, is_omitted
