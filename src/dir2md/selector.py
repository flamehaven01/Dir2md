"""Candidate selection, sampling, and deduplication."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from .masking import apply_masking
from .simhash import simhash64, hamming
from .summary import summarize
from .search import match_query_snippet
from .samplers.semantic import SemanticSampler

SINGLE_FILE_MAX_BYTES = 1 * 1024 * 1024  # 1MB guard per file


def build_candidates(cfg, files: List[Path], root: Path, is_included, is_omitted) -> Tuple[List[dict], Dict[Path, str]]:
    candidates: list[dict] = []
    sim_seen: list[int] = []
    candidate_hash: dict[Path, str] = {}

    for f in files:
        if cfg.only_ext and f.suffix.lstrip(".").lower() not in cfg.only_ext:
            continue
        if is_omitted(f):
            continue
        if not is_included(f):
            continue
        if f.is_symlink():
            if not cfg.follow_symlinks:
                continue
            try:
                resolved = f.resolve(strict=False)
            except (OSError, RuntimeError):
                continue
            try:
                resolved.relative_to(root)
            except ValueError:
                continue

        try:
            size = f.stat().st_size
        except OSError:
            continue

        if size > SINGLE_FILE_MAX_BYTES:
            print(f"[WARN] Skipping {f} ({size} bytes > {SINGLE_FILE_MAX_BYTES} bytes limit)")
            text = f"<Skipped: File too large ({size} bytes > {SINGLE_FILE_MAX_BYTES} bytes limit)>"
            placeholder_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            match_score = 0
            snippet = ""
            if cfg.query:
                match_score, snippet = match_query_snippet(text, cfg.query)
            sh = simhash64(text)
            if cfg.dedup_bits > 0 and any(hamming(sh, h0) <= cfg.dedup_bits for h0 in sim_seen):
                continue
            sim_seen.append(sh)
            candidates.append({
                "path": f,
                "sha256": placeholder_hash,
                "summary": summarize(f, text, max_lines=10),
                "text": text,
                "simhash": sh,
                "match_score": match_score,
                "snippet": snippet,
            })
            candidate_hash[f] = placeholder_hash
            continue

        try:
            h = hashlib.sha256()
            collected = bytearray()
            limit = cfg.max_bytes
            with f.open("rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    h.update(chunk)
                    if limit is None or len(collected) < limit:
                        if limit is None:
                            collected.extend(chunk)
                        else:
                            remaining = limit - len(collected)
                            if remaining > 0:
                                collected.extend(chunk[:remaining])
            full_file_hash = h.hexdigest()
            raw = bytes(collected)
        except Exception:
            continue

        text = raw.decode("utf-8", errors="replace")
        if cfg.masking_mode != "off" or cfg.custom_mask_patterns:
            text = apply_masking(text, mode=cfg.masking_mode, custom_patterns=cfg.custom_mask_patterns)

        # Phase 3: AST semantic sampling (auto-enabled for Python files in ai/pro presets)
        if cfg.preset in ['ai', 'pro'] and str(f).endswith('.py') and len(text) > 500:
            sampler = SemanticSampler(preserve_ratio=0.6 if cfg.preset == 'ai' else 0.7)
            sampled_text, stats = sampler.sample_python_code(text)
            if stats['method'] == 'ast_semantic' and stats['reduction'] > 10:
                text = sampled_text
                # Note: Semantic sampling applied with {stats['reduction']:.1f}% reduction

        match_score = 0
        snippet = ""
        if cfg.query:
            match_score, snippet = match_query_snippet(text, cfg.query)
        sh = simhash64(text)
        if cfg.dedup_bits > 0 and any(hamming(sh, h0) <= cfg.dedup_bits for h0 in sim_seen):
            continue
        sim_seen.append(sh)
        candidates.append({
            "path": f,
            "sha256": full_file_hash,
            "summary": summarize(f, text, max_lines=40),
            "text": text,
            "simhash": sh,
            "match_score": match_score,
            "snippet": snippet,
        })
        candidate_hash[f] = full_file_hash

    if cfg.query:
        matched = [rec for rec in candidates if rec.get("match_score", 0) > 0]
        if matched:
            candidates = matched
        candidates.sort(key=lambda rec: rec.get("match_score", 0), reverse=True)

    return candidates, candidate_hash
