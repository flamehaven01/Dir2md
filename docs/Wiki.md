# Dir2md + Spicy: Turn Any Repo into LLM-Ready Context (and Catch Risks)

## What it does (TL;DR)
- Scans a repo and produces both **human-friendly Markdown** and **LLM-ready JSON/JSONL** in one shot.
- **NEW v1.2.1**: Enterprise-grade security (5 critical fixes) + flexible 3-tier configuration system.
- **NEW v1.2.0**: Zero-config intelligence (60-70% token reduction) with Gravitas compression, smart query, and AST sampling.
- Smart sampling + token budgeting to avoid overloading models.
- Built-in masking for secrets and a **Spicy** 5-level risk report (on by default).

**SIDRCE Grade: A (90-94/100)** — Security: A+ | Reliability: A | Performance: A

## Why developers should care
- **Onboarding**: New teammates see the structure, key files, and summaries in under a minute.
- **PR / Code Review**: Drop the JSONL straight into your LLM to review a large codebase without token waste.
- **Safety & Quality**: Spicy highlights risky spots; masking protects tokens/keys/PEM/JWT/DB URLs.
- **Reproducible**: Cache/venv noise auto-excluded; `--no-timestamp` keeps outputs stable for CI.
- **NEW v1.2.1**: Enterprise security (Markdown injection prevention, RCE elimination) + flexible configuration.
- **NEW v1.2.0**: Automatic 60-70% token reduction with zero configuration overhead.

## Key technical bits

### Intelligence (v1.2.0)
- **Gravitas Compression**: 30-50% token reduction using symbolic compression (auto-enabled in `pro`/`ai`)
- **Smart Query Processing**: Typo correction + synonym expansion, 60%→90% accuracy (auto-enabled with queries)
- **AST Semantic Sampling**: Python structure extraction, 30-40% additional reduction (auto-enabled for .py files)

### Security & Configuration (v1.2.1)
- **Security Fixes**: 5 critical issues resolved (Markdown injection, RCE, silent failures, glob expansion, externalized config)
- **3-Tier Priority System**: User CLI > Project config (pyproject.toml) > System defaults (defaults.json)
- **Flexible Configuration**: `--defaults-file` for custom defaults, `[tool.dir2md.excludes]` for project-level patterns

### Core Features
- **Sampling & Budgets**: Head/tail sampling, token estimates; auto-skip when budgets would overflow.
- **SimHash Dedup**: Filters near-duplicate files/build artifacts.
- **Masking**: Basic & advanced patterns (keys, tokens, JWT, DB URLs, PEM, Slack/GitHub tokens) + custom regex.
- **Spicy Risk Report**: 5 severities (ok/warn/risk/high/critical), score+counts+per-file findings. `--spicy-strict` makes CI fail on high/critical.
- **Modular pipeline**: `walker` (tree/filter) → `selector` (sampling/SimHash) → `renderer` (md/json/jsonl) → `orchestrator` (multi-format).

## Outputs
- **Markdown (.md)**: Tree, selected snippets, stats, Spicy table (file, line, severity, message, suggestion).
- **JSON (.json)**: Structured manifest of files/stats/spicy for downstream tools.
- **JSONL (.jsonl)**: One line per file (path, content/snippet, meta) plus spicy summary — ideal for LLM ingest/vector DB.

## Defaults you get out of the box
- **v1.2.1**: Flexible 3-tier exclusion system (user > project > system defaults)
- **v1.2.0**: Auto-enabled intelligence (Gravitas + Smart Query + AST in `pro`/`ai` presets)
- Spicy ON (disable with `--no-spicy`; gate with `--spicy-strict`)
- Dual outputs (md + jsonl)
- Noise auto-excluded: `.pytest_cache`, `.ruff_cache`, `venv_clean`, etc. (configurable via `defaults.json`)
- UTF-8 writes; human md + machine jsonl in one run

## Presets
| preset | mode | budget | best for |
| --- | --- | --- | --- |
| `pro` (default) | summary/ref | user-set | balanced CI/PR context |
| `raw` | inline | unlimited | full code visibility |
| `ai` | ref | 6000 cap | LLM-focused, query-prioritized |
| `fast` | off (no contents) | n/a | ultra-light tree + manifest |

## Typical runs
```bash
# Default: md + jsonl, spicy on, auto-intelligence
dir2md .

# Ultra-light for PR comment (tree + manifest only)
dir2md . --fast

# Query-focused LLM context with all optimizations (v1.2.0)
dir2md . --ai-mode --query "auth flow" --output-format jsonl
# Auto: typo correction + expansion + gravitas medium + AST sampling

# Enforce failure on high/critical risks
dir2md . --spicy --spicy-strict

# NEW v1.2.1: Custom configuration
dir2md . --defaults-file my-defaults.json  # Custom system defaults
dir2md . --exclude-glob "secret-data/"     # User override (highest priority)

# NEW v1.2.1: Project-level config in pyproject.toml
# [tool.dir2md]
# excludes = ["*.log", "temp/", "cache/"]
dir2md .  # Automatically uses project config
```

## CI / pipelines
- Use `--output-format jsonl` for direct LLM ingestion.
- Use `--fast` + artifact upload for PR context.
- Add `--spicy-strict` as a quality gate.
- **v1.2.1**: Use `--defaults-file` for CI-specific exclusion patterns.
- **v1.2.0**: Use `--ai-mode` for maximum token efficiency (60-70% reduction).

## Why it feels good to use
- **Saves time**: No manual tree/sampling; outputs tailored for humans and LLMs simultaneously.
- **Reduces risk**: Masking + Spicy risk surfacing by default; v1.2.1 eliminates critical security vulnerabilities.
- **Minimal setup**: Caches/venvs ignored by default; reproducible outputs.
- **Intelligent**: v1.2.0 auto-optimizations reduce tokens by 60-70% with zero configuration.
- **Flexible**: v1.2.1 3-tier configuration system adapts to any workflow (user > project > system).
- **Production-ready**: SIDRCE Grade A (90-94/100) with enterprise-grade quality.

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
