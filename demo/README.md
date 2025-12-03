---
title: dir2md + Spicy - Repository to Markdown Converter
emoji: 📂
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 5.45.0
app_file: app.py
pinned: false
license: mit
short_description: Markdown + spicy risk blueprints for GitHub repos
tags:
  - developer-tools
  - markdown
  - repository-analysis
  - llm
  - code-analysis
  - python
---

# dir2md + Spicy (Hugging Face Demo)

Convert any public GitHub repository into an LLM-ready markdown blueprint plus optional spicy (5-level) risk report.

## What the demo does
- Analyze repo structure and key files.
- Generate tree + sampled content with token-aware budgets.
- Output human markdown and JSONL (for LLMs), with optional spicy findings.

## Quick start
1) Paste a GitHub URL.  
2) Choose options: include contents, emit manifest, enable spicy/strict.  
3) Run and download the markdown/JSONL outputs.

## Fresh highlights (1.1.0)
- `--fast` preset (tree + manifest only, no file reads).
- Default dual outputs (md + jsonl) for human + LLM.
- Spicy risk report (`--spicy`, `--spicy-strict`) with 5 severity levels.
- Modular pipeline (`walker`, `selector`, `renderer`, `orchestrator`) for cleaner extensibility.

## Notes
- Current Gradio SDK: **5.45.0**. A newer **6.0.2** is available; update `sdk_version` and `gradio` pin if you want to try it.
- App entrypoint: `demo/app.py`; deps in `demo/requirements.txt`.

Made with care by Flamehaven for developers who want their AI to understand their code.

