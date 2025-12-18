"""Spicy risk evaluator for dir2md."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

SPICY_LEVELS = ["ok", "warn", "risk", "high", "critical"]
LEVEL_TO_CHILI = {
    "ok": "⚪️",
    "warn": "🌶",
    "risk": "🌶🌶",
    "high": "🌶🌶🌶🌶",
    "critical": "🌶🌶🌶🌶🌶",
}


@dataclass
class Finding:
    file: str
    line: int
    severity: str  # ok|warn|risk|high|critical
    category: str
    message: str
    suggestion: str
    score: int


def _add(findings: List[Finding], level: str, category: str, message: str, suggestion: str, file: str = "-", line: int = 0, score: int = 0) -> None:
    findings.append(
        Finding(
            file=file,
            line=line,
            severity=level,
            category=category,
            message=message,
            suggestion=suggestion,
            score=score,
        )
    )


def evaluate_spicy(cfg, stats, candidates, selected_blocks) -> Tuple[int, Dict[str, int], List[Finding]]:
    """
    Evaluate simple rule-based risk and produce severity counts and findings.
    Returns (score 0-100, counts dict, findings list).
    """
    findings: List[Finding] = []
    score = 0

    def bump(level: str, delta: int, category: str, message: str, suggestion: str, file: str = "-", line: int = 0):
        nonlocal score
        _add(findings, level, category, message, suggestion, file=file, line=line, score=delta)
        score += delta

    # Rules
    if cfg.masking_mode == "off" and cfg.preset != "raw":
        bump("high", 20, "security", "masking is off in non-raw preset (secrets may leak)", "use --masking basic or advanced")

    # NOTE: Phantom Code Detection via external tools (like vulture) removed in v1.2.1
    # Reason: Security risk (RCE vector via malicious binary in PATH) + unreliable dependency
    # Future: Implement dead code detection using AST analysis or vulture library API (not subprocess)

    if cfg.follow_symlinks:
        # rough: if any candidate path escapes root we already skipped; still warn
        bump("risk", 10, "path", "follow_symlinks enabled can traverse out of repo", "disable --follow-symlinks unless required")

    if cfg.emit_manifest is False and cfg.preset != "raw":
        bump("warn", 5, "tracking", "manifest disabled; provenance tracking reduced", "enable --emit-manifest")

    if cfg.include_contents and cfg.max_bytes and cfg.max_bytes > 500_000:
        bump("warn", 5, "performance", "max_bytes set very high; large files may be ingested", "lower --max-bytes or use --fast/--omit-glob")

    if cfg.query and not any(rec.get("match_score", 0) > 0 for rec in candidates):
        bump("warn", 5, "relevance", "query provided but no files matched", "adjust --query or include_glob/only_ext")

    # counts by severity
    counts: Dict[str, int] = {k: 0 for k in SPICY_LEVELS}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    # clamp score
    score = max(0, min(100, score))
    return score, counts, findings
