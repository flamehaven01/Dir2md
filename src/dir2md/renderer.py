"""Render file selections into markdown/json/jsonl."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from .markdown import to_markdown
from .token import estimate_tokens
from .spicy import LEVEL_TO_CHILI


def render_blocks(cfg, root: Path, candidates: List[dict]) -> Tuple[List[tuple], List[dict], int]:
    est_total = 0
    selected_blocks: list[tuple[Path, str, str]] = []
    selected_hashes: list[int] = []
    json_entries: list[dict] = []

    def drift_score_bits(sh: int) -> int:
        if not selected_hashes:
            return 64
        return min((sh ^ prev).bit_count() for prev in selected_hashes)  # type: ignore[arg-type]

    for rec in candidates:
        if cfg.llm_mode == "off":
            break
        sh = rec["simhash"]
        drift_bits = drift_score_bits(sh)
        drift = round(drift_bits / 64, 3)
        if cfg.llm_mode == "ref":
            meta_payload = {"sha256": rec["sha256"], "path": str(rec["path"]), "drift": drift}
            if cfg.query:
                meta_payload["query"] = cfg.query
                if rec.get("match_score"):
                    meta_payload["match_score"] = rec["match_score"]
                if rec.get("snippet"):
                    meta_payload["snippet"] = rec["snippet"]
            meta = json.dumps(meta_payload, ensure_ascii=False)
            tok = estimate_tokens(meta) + 16
            if est_total + tok > cfg.budget_tokens:
                continue
            est_total += tok
            selected_blocks.append((rec["path"], "json", meta))
            selected_hashes.append(sh)
            json_entries.append({
                "path": str(rec["path"].relative_to(root)),
                "mode": cfg.llm_mode,
                "lang": "json",
                "sha256": rec["sha256"],
                "match_score": rec.get("match_score", 0),
                "snippet": rec.get("snippet", ""),
                "content": meta_payload,
            })
        elif cfg.llm_mode == "summary":
            payload = rec["summary"]
            tok = estimate_tokens(payload)
            if est_total + tok > cfg.budget_tokens:
                continue
            est_total += tok
            text = payload
            if cfg.query and rec.get("snippet"):
                text += f"\n\n<!-- query: {rec['snippet']} -->"
            if cfg.explain_capsule:
                text += f"\n\n<!-- why: summary; drift={drift} -->"
            selected_blocks.append((rec["path"], "markdown", text))
            selected_hashes.append(sh)
            json_entries.append({
                "path": str(rec["path"].relative_to(root)),
                "mode": cfg.llm_mode,
                "lang": "markdown",
                "sha256": rec["sha256"],
                "match_score": rec.get("match_score", 0),
                "snippet": rec.get("snippet", ""),
                "content": text,
            })
        else:  # inline
            lines = rec["text"].splitlines()
            if cfg.max_lines and len(lines) > cfg.max_lines:
                lines = lines[: cfg.max_lines]
            content = "\n".join(lines)
            if estimate_tokens(content) > cfg.max_file_tokens:
                head = lines[: cfg.sample_head]
                tail = lines[-cfg.sample_tail:] if cfg.sample_tail > 0 else []
                mid = f"\n<!-- [truncated middle: {max(0, len(lines)-len(head)-len(tail))} lines omitted] -->\n"
                content = "\n".join(head + [mid] + tail)
            tok = min(cfg.max_file_tokens, estimate_tokens(content))
            if est_total + tok > cfg.budget_tokens:
                continue
            est_total += tok
            if cfg.query and rec.get("snippet"):
                content = f"<!-- query: {rec['snippet']} -->\n{content}"
            if cfg.explain_capsule:
                content += f"\n\n<!-- why: inline; drift={drift}; tok={tok} -->"
            lang = rec["path"].suffix.lstrip(".") or "text"
            selected_blocks.append((rec["path"], lang, content))
            selected_hashes.append(sh)
            json_entries.append({
                "path": str(rec["path"].relative_to(root)),
                "mode": cfg.llm_mode,
                "lang": lang,
                "sha256": rec["sha256"],
                "match_score": rec.get("match_score", 0),
                "snippet": rec.get("snippet", ""),
                "content": content,
            })

    return selected_blocks, json_entries, est_total


def render_json(cfg, root: Path, stats, json_entries, spicy_bundle):
    payload = {
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
    }
    if spicy_bundle:
        payload["spicy"] = spicy_bundle
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_jsonl(json_entries, spicy_bundle):
    lines = [json.dumps(entry, ensure_ascii=False) for entry in json_entries]
    if spicy_bundle:
        lines.append(json.dumps({"spicy": spicy_bundle}, ensure_ascii=False))
    return "\n".join(lines)


def build_manifest(cfg, stats, selected_blocks, root: Path, candidate_hash: Dict[Path, str], spicy_bundle):
    """Assemble manifest dictionary for writing or downstream use."""
    file_manifest = []
    for (p, _, t) in selected_blocks:
        try:
            entry = {"path": str(p.relative_to(root)), "mode": cfg.llm_mode}
        except ValueError:
            continue
        entry["sha256"] = candidate_hash.get(p)
        if p.suffix.lower() == ".json":
            try:
                meta = json.loads(t)
                entry.update(meta)
            except Exception:
                pass
        file_manifest.append(entry)
    full_manifest = {
        "stats": {
            "total_dirs": stats.total_dirs,
            "total_files_in_tree": stats.total_files_in_tree,
            "total_omitted": stats.total_omitted,
            "total_with_contents": stats.total_with_contents,
            "est_tokens_prompt": stats.est_tokens_prompt,
        },
        "files": file_manifest,
    }
    if spicy_bundle:
        full_manifest["spicy"] = spicy_bundle
    return full_manifest


def render_spicy_md(md_output: str, spicy_counts: Dict[str, int], spicy_score: int, spicy_findings: List[dict]) -> str:
    chili = LEVEL_TO_CHILI.get(
        "critical" if spicy_counts.get("critical") else
        "high" if spicy_counts.get("high") else
        "risk" if spicy_counts.get("risk") else
        "warn" if spicy_counts.get("warn") else "ok",
        "⚪️",
    )
    lines = [md_output, "## Spicy Review", f"- Spicy Level: {chili}  score={spicy_score}/100"]
    if spicy_counts:
        lines.append(f"- Counts: {spicy_counts}")
    if spicy_findings:
        lines.append("")
        lines.append("| file | line | severity | category | message | suggestion |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for f in spicy_findings:
            chili_cell = LEVEL_TO_CHILI.get(f["severity"], f["severity"])
            lines.append(
                f"| {f['file']} | {f['line']} | {chili_cell} {f['severity']} | "
                f"{f['category']} | {f['message']} | {f['suggestion']} |"
            )
    return "\n".join(lines)


def render_markdown(cfg, tree_lines, selected_blocks, stats):
    return to_markdown(cfg, tree_lines, selected_blocks, stats)
