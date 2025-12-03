"""Pipeline orchestrator to centralize report generation across formats."""
from __future__ import annotations

from typing import Dict, List

from .core import Config, generate_markdown_report


def run_pipeline(cfg: Config, formats: List[str]) -> Dict[str, str]:
    """Generate outputs for multiple formats using a single config."""
    outputs: Dict[str, str] = {}
    for fmt in formats:
        cfg.output_format = fmt
        outputs[fmt] = generate_markdown_report(cfg)
    return outputs
