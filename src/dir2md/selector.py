"""Candidate selection, sampling, and deduplication."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

from .masking import apply_masking
from .simhash import simhash64, hamming
from .summary import summarize
from .search import match_query_snippet


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
