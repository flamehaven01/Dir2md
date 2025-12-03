from dir2md.spicy import evaluate_spicy
from dir2md.core import Config, Stats
from pathlib import Path


def dummy_cfg():
    return Config(
        root=Path("."),
        output=Path("OUT.md"),
        include_globs=[],
        exclude_globs=[],
        omit_globs=[],
        respect_gitignore=False,
        follow_symlinks=False,
        max_bytes=1000,
        max_lines=100,
        include_contents=True,
        add_stats=True,
        add_toc=False,
        llm_mode="ref",
        budget_tokens=100,
        max_file_tokens=50,
        dedup_bits=0,
        sample_head=5,
        sample_tail=3,
        strip_comments=False,
        emit_manifest=False,
        preset="pro",
        explain_capsule=False,
        no_timestamp=True,
        masking_mode="off",
        custom_mask_patterns=[],
        query=None,
        output_format="md",
        spicy=True,
    )


def test_spicy_warn_masking_off():
    cfg = dummy_cfg()
    stats = Stats()
    score, counts, findings = evaluate_spicy(cfg, stats, [], [])
    assert score >= 5
    assert counts.get("warn", 0) >= 1
    assert any("masking" in f.message for f in findings)
