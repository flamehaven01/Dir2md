from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import Config, Stats


def _escape_fence(text: str, lang: str = "") -> tuple[str, str]:
    """
    Escape markdown code fences to prevent injection.
    If text contains ```, use ```` (or more) for outer fence.
    Returns (fence_marker, escaped_text).
    """
    # Count consecutive backticks in text
    max_backticks = 0
    current_backticks = 0
    for char in text:
        if char == '`':
            current_backticks += 1
            max_backticks = max(max_backticks, current_backticks)
        else:
            current_backticks = 0

    # Use one more backtick than the maximum found
    fence_length = max(3, max_backticks + 1)
    fence = '`' * fence_length

    return fence, text


def to_markdown(cfg: 'Config', tree_lines: list[str], file_blocks: list[tuple[Path, str, str]], stats: 'Stats') -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts: list[str] = []
    parts.append("# Project Blueprint\n")
    parts.append(f"- Root: `{cfg.root}`  ")
    if not cfg.no_timestamp:
        parts.append(f"- Generated: `{ts}`  ")
    parts.append(f"- Preset: `{cfg.preset}`  ")
    parts.append(f"- LLM mode: `{cfg.llm_mode}`  ")
    parts.append(f"- Estimated tokens (prompt): `{stats.est_tokens_prompt}`  ")
    parts.append("")
    parts.append("## Directory Tree\n")
    # Tree lines are safe (no user content), use standard fence
    parts.append("```\n" + "\n".join(tree_lines) + "\n```\n\n")
    if cfg.llm_mode != "off" and file_blocks:
        parts.append("## File Contents\n")
        for path, lang, text in file_blocks:
            rel = path.relative_to(cfg.root)
            parts.append(f"### File: `{rel}`\n")
            # Escape fence to prevent markdown injection
            fence, escaped_text = _escape_fence(text, lang)
            parts.append(f"{fence}{lang}\n{escaped_text}\n{fence}\n\n")
    if cfg.add_stats:
        parts.append("## Summary\n")
        parts.append("| metric | value |\n|---|---:|")
        parts.append(f"| dirs | {stats.total_dirs} |")
        parts.append(f"| files in tree | {stats.total_files_in_tree} |")
        parts.append(f"| selected files | {stats.total_with_contents} |")
        parts.append(f"| omitted | {stats.total_omitted} |")
        parts.append(f"| est tokens (prompt) | {stats.est_tokens_prompt} |\n")
    return "\n".join(parts)