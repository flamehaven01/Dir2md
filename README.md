# Dir2md +Spicy

<p align="center">
  <img src="./docs/dir2md-logo.png" alt="Dir2md Logo" width="400">
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href=".github/workflows/release.yml"><img src="https://img.shields.io/badge/CI%2FCD-release%20workflow-blue" alt="CI/CD"></a>
</p>

<p align="center">
  <strong>Transform your codebase into LLM-optimized markdown blueprints</strong>
</p>

Dir2md converts directory structures into AI-friendly markdown with intelligent content sampling, security masking, and token-budget control—perfect for AI-assisted development.

## Quick Start

**New to Dir2md?** Check out **[Wiki.md](docs/Wiki.md)** for a friendly introduction with examples.

### Try Online
[**Dir2md Demo on Hugging Face Spaces**](https://huggingface.co/spaces/Flamehaven/dir2md-demo) — No installation required

### Installation

```bash
# From PyPI
pip install dir2md

# From GitHub (latest features)
git clone https://github.com/Flamehaven/dir2md.git
cd dir2md
pip install -e .
```

### Basic Usage

```bash
# Generate markdown blueprint
dir2md .

# LLM-optimized with token budget
dir2md . --ai-mode --budget-tokens 4000

# Security-focused with query ranking
dir2md . --masking basic --query "authentication"
```

## Key Features

- **Smart Sampling** — Head/tail content sampling with configurable token budgets
- **Security Masking** — Automatic detection of API keys, tokens, credentials, PEM blocks
- **AI Optimization** — Query-based ranking, JSONL output, LLM-friendly formatting
- **Risk Analysis** — Built-in security scanning with 5-level severity findings
- **Flexible Output** — Markdown, JSON, JSONL, and manifest formats
- **Custom Patterns** — Extensible masking via CLI, files, or `pyproject.toml`

## Configuration

### Presets

| Preset | Token Budget | Best For |
|--------|--------------|----------|
| `raw` | Unlimited | Full code review, development |
| `pro` | User-defined | Production with custom budgets |
| `ai` | 6000 | LLM context with query ranking |
| `fast` | Minimal | Tree structure + manifest only |

### Configuration File

Create `pyproject.toml` in your project root:

```toml
[tool.dir2md]
preset = "pro"
budget_tokens = 8000
include_glob = ["src/**/*.py", "tests/**/*.py"]
exclude_glob = ["**/__pycache__/**"]
emit_manifest = true

[tool.dir2md.masking]
level = "basic"
patterns = ["(?i)custom_secret_\\w+"]
```

**Learn more:** [CLI Reference](docs/CLI_REFERENCE.md) | [Features](docs/FEATURES.md)

## Common Commands

```bash
# AI/LLM context generation
dir2md . --ai-mode --query "authentication" --budget-tokens 6000

# Security audit with masking
dir2md . --masking advanced --spicy-strict

# CI/CD integration
dir2md . --preset pro --emit-manifest --no-timestamp

# Quick preview
dir2md . --preset fast --dry-run
```

**Full reference:** [`dir2md --help`](docs/CLI_REFERENCE.md)

## Docker

```bash
# Build image
docker build -t dir2md:local .

# Run (Windows)
docker run --rm -v %cd%:/work dir2md:local /work --ai-mode

# Run (Linux/macOS)
docker run --rm -v $PWD:/work dir2md:local /work --ai-mode
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/Flamehaven/dir2md.git
cd dir2md
pip install -e ".[dev]"
python -m pytest -v
```

### Reporting Issues

- **Bugs**: [GitHub Issues](https://github.com/Flamehaven/dir2md/issues)
- **Features**: [GitHub Discussions](https://github.com/Flamehaven/dir2md/discussions)
- **Security**: info@flamehaven.space

## Documentation

- **[CLI Reference](docs/CLI_REFERENCE.md)** — Complete command-line options
- **[Features](docs/FEATURES.md)** — Detailed feature documentation
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** — Common issues and solutions
- **[Usage Examples](USAGE_EXAMPLES.md)** — Quick copy-paste recipes
- **[Contributing](CONTRIBUTING.md)** — Development guidelines

## Quality & Certification

**SIDRCE Certified** — ID: SIDRCE-DIR2MD-20251203-ARCHON  
Integrity: 98 | Resonance: 95 | Stability: 95 | Overall: 96/100

Architecture follows distributed responsibility patterns with comprehensive test coverage and deterministic cross-platform behavior.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

This project shares its name with [IsaacBreen's dir2md](https://pypi.org/project/dir2md/), a simpler directory-to-markdown tool. Our enhanced version focuses on LLM optimization, token budgeting, and security masking for AI-assisted development.

---

<p align="center">
  Made with care by <strong>Flamehaven</strong> for developers who want their AI to understand their code
</p>
