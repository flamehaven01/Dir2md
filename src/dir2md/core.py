"""Core config and generation orchestrator helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import json

from .manifest import write_manifest
from .spicy import evaluate_spicy
from .walker import collect_files
from .selector import build_candidates
from .renderer import (
    render_blocks,
    build_manifest,
    render_markdown,
    render_spicy_md,
)


@dataclass
class Stats:
    total_dirs: int = 0
    total_files_in_tree: int = 0
    total_omitted: int = 0
    total_with_contents: int = 0
    est_tokens_prompt: int = 0


@dataclass
class Config:
    root: Path
    output: Path
    include_globs: List[str]
    exclude_globs: List[str]
    omit_globs: List[str]
    respect_gitignore: bool
    follow_symlinks: bool
    max_bytes: Optional[int]
    max_lines: Optional[int]
    include_contents: bool
    only_ext: Optional[set[str]] = None
    add_stats: bool = True
    add_toc: bool = False
    llm_mode: str = "ref"
    budget_tokens: int = 6000
    max_file_tokens: int = 1200
    dedup_bits: int = 16
    sample_head: int = 120
    sample_tail: int = 40
    strip_comments: bool = False
    emit_manifest: bool = True
    preset: str = "pro"
    explain_capsule: bool = False
    no_timestamp: bool = False
    masking_mode: str = "basic"
    custom_mask_patterns: List[str] = field(default_factory=list)
    query: Optional[str] = None
    output_format: str = "md"
    spicy: bool = False


_DEFAULT_ONLY_EXT = {"py", "ts", "tsx", "js", "jsx", "md", "txt", "toml", "yaml", "yml", "json", ""}


def _estimate_total_bytes(cfg: Config) -> int:
    total_bytes = 0
    max_cap = 10_000_000
    for f in cfg.root.rglob('*'):
        if f.is_file():
            try:
                total_bytes += f.stat().st_size
            except OSError:
                continue
            if total_bytes >= max_cap:
                break
    return total_bytes


def apply_preset(cfg: Config) -> Config:
    try:
        _estimate_total_bytes(cfg)
    except Exception:
        pass
    if cfg.preset == "raw":
        cfg.llm_mode = "inline"
        cfg.dedup_bits = 0
        cfg.only_ext = None
        cfg.emit_manifest = False
    elif cfg.preset == "pro":
        cfg.llm_mode = cfg.llm_mode or "summary"
    elif cfg.preset == "fast":
        cfg.llm_mode = "off"
        cfg.dedup_bits = 16
        cfg.emit_manifest = True
        cfg.include_contents = False
        cfg.output_format = "md"
    return cfg


def generate_markdown_report(cfg: Config) -> str:
    cfg = apply_preset(cfg)
    root = cfg.root
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    stats = Stats()
    files, tree_lines, is_included, is_omitted = collect_files(
        root,
        cfg.include_globs,
        cfg.exclude_globs,
        cfg.omit_globs,
        cfg.respect_gitignore,
        cfg.follow_symlinks,
        stats,
    )

    candidates, candidate_hash = build_candidates(cfg, files, root, is_included, is_omitted)
    selected_blocks, json_entries, est_total = render_blocks(cfg, root, candidates)

    stats.total_files_in_tree = len(files)
    stats.total_omitted = max(0, len(files) - len(selected_blocks))
    stats.total_with_contents = len(selected_blocks)
    stats.est_tokens_prompt = est_total

    spicy_score = 0
    spicy_counts = {}
    spicy_findings = []
    spicy_bundle = None
    if cfg.spicy:
        spicy_score, spicy_counts, spicy_findings = evaluate_spicy(cfg, stats, candidates, selected_blocks)
        spicy_rows = [f.__dict__ if hasattr(f, "__dict__") else f for f in spicy_findings]
        spicy_bundle = {
            "score": spicy_score,
            "counts": spicy_counts,
            "findings": spicy_rows,
        }
        cfg.spicy_score = spicy_score  # type: ignore[attr-defined]
        cfg.spicy_counts = spicy_counts  # type: ignore[attr-defined]

    if cfg.emit_manifest:
        full_manifest = build_manifest(cfg, stats, selected_blocks, root, candidate_hash, spicy_bundle)
        write_manifest(full_manifest, cfg.output.with_suffix('.manifest.json'))

    if cfg.output_format == "json":
        return json.dumps(
            {
                "root": str(cfg.root),
                "preset": cfg.preset,
                "llm_mode": cfg.llm_mode,
                "stats": {
                    "total_dirs": stats.total_dirs,
                    "total_files_in_tree": stats.total_files_in_tree,
                    "total_omitted": stats.total_omitted,
                    "total_with_contents": stats.total_with_contents,
                    "est_tokens_prompt": stats.est_tokens_prompt,
                },
                "files": json_entries,
                "spicy": spicy_bundle,
            },
            ensure_ascii=False,
            indent=2,
        )

    if cfg.output_format == "jsonl":
        lines = [json.dumps(entry, ensure_ascii=False) for entry in json_entries]
        if spicy_bundle:
            lines.append(json.dumps({"spicy": spicy_bundle}, ensure_ascii=False))
        return "\n".join(lines)

    md_output = render_markdown(cfg, tree_lines, selected_blocks, stats)
    if cfg.spicy and spicy_bundle:
        md_output = render_spicy_md(md_output, spicy_counts, spicy_score, spicy_bundle["findings"])

    return md_output
