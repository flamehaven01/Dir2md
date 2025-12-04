# Dir2md + Spicy: Turn Any Repo into LLM-Ready Context (and Catch Risks)

## What it does (TL;DR)
- Scans a repo and produces both **human-friendly Markdown** and **LLM-ready JSON/JSONL** in one shot.
- Smart sampling + token budgeting to avoid overloading models.
- Built-in masking for secrets and a **Spicy** 5-level risk report (on by default).

## Why developers should care
- **Onboarding**: New teammates see the structure, key files, and summaries in under a minute.
- **PR / Code Review**: Drop the JSONL straight into your LLM to review a large codebase without token waste.
- **Safety & Quality**: Spicy highlights risky spots; masking protects tokens/keys/PEM/JWT/DB URLs.
- **Reproducible**: Cache/venv noise auto-excluded; `--no-timestamp` keeps outputs stable for CI.

## Key technical bits
- **Sampling & Budgets**: Head/tail sampling, token estimates; auto-skip when budgets would overflow.
- **SimHash Dedup**: Filters near-duplicate files/build artifacts.
- **Masking**: Basic & advanced patterns (keys, tokens, JWT, DB URLs, PEM, Slack/GitHub tokens) + custom regex.
- **Spicy Risk Report**: 5 severities (ok/warn/risk/high/critical), score+counts+per-file findings in md/json/jsonl/manifest. `--spicy-strict` makes CI fail on high/critical.
- **Modular pipeline**: `walker` (tree/filter) → `selector` (sampling/SimHash) → `renderer` (md/json/jsonl) → `orchestrator` (multi-format).

## Outputs
- **Markdown (.md)**: Tree, selected snippets, stats, Spicy table (file, line, severity, message, suggestion).
- **JSON (.json)**: Structured manifest of files/stats/spicy for downstream tools.
- **JSONL (.jsonl)**: One line per file (path, content/snippet, meta) plus spicy summary — ideal for LLM ingest/vector DB.

## Defaults you get out of the box
- Spicy ON (disable with `--no-spicy`; gate with `--spicy-strict`).
- Dual outputs (md + jsonl).
- Noise auto-excluded: `.pytest_cache`, `.pytest_cache_local`, `.ruff_cache`, `venv_clean`, etc.
- UTF-8 writes; human md + machine jsonl in one run.

## Presets
| preset | mode | budget | best for |
| --- | --- | --- | --- |
| `pro` (default) | summary/ref | user-set | balanced CI/PR context |
| `raw` | inline | unlimited | full code visibility |
| `ai` | ref | 6000 cap | LLM-focused, query-prioritized |
| `fast` | off (no contents) | n/a | ultra-light tree + manifest |

## Typical runs
```bash
# Default: md + jsonl, spicy on
dir2md .

# Ultra-light for PR comment (tree + manifest only)
dir2md . --fast

# Query-focused LLM context with spicy
dir2md . --ai-mode --query "auth flow" --output-format jsonl

# Enforce failure on high/critical risks
dir2md . --spicy --spicy-strict
```

## CI / pipelines
- Use `--output-format jsonl` for direct LLM ingestion.
- Use `--fast` + artifact upload for PR context.
- Add `--spicy-strict` as a quality gate.

## Why it feels good to use
- Saves time: no manual tree/sampling; outputs tailored for humans and LLMs simultaneously.
- Reduces risk: masking + spicy risk surfacing by default.
- Minimal setup: caches/venvs ignored by default; reproducible outputs.

---

## Learn More

### Complete Documentation
- **[CLI Reference](CLI_REFERENCE.md)** - All commands, options, and examples
- **[Features Guide](FEATURES.md)** - Technical capabilities and architecture details
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Links
- [Main README](../README.md) - Project overview
- [Usage Examples](../USAGE_EXAMPLES.md) - Copy-paste recipes
- [Contributing](../CONTRIBUTING.md) - Development guidelines

### Community & Support
- [GitHub Issues](https://github.com/Flamehaven/dir2md/issues) - Bug reports
- [GitHub Discussions](https://github.com/Flamehaven/dir2md/discussions) - Questions and ideas
- Email: info@flamehaven.space (security issues)

---

Made for developers who want their AI to actually understand their code. 
