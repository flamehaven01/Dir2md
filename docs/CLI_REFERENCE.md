# CLI Reference

Complete command-line interface documentation for Dir2md.

**Quick Start:** [Wiki.md](Wiki.md) | **Main:** [README](../README.md) | **Features:** [FEATURES.md](FEATURES.md) | **Help:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Basic Syntax

```bash
dir2md [PATH] [OPTIONS]
```

## Core Options

### Output Configuration
- `-o, --output FILE` - Output file path (default: auto-generated)
- `--output-format [md|json|jsonl]` - Output format
- `--emit-manifest` - Generate .manifest.json metadata file
- `--no-timestamp` - Omit timestamp from filenames (CI-friendly)

### Presets
- `--preset [raw|pro|ai|fast]` - Quick configuration profiles

| Preset | Token Budget | Mode | Best For |
|--------|--------------|------|----------|
| `raw` | Unlimited | inline | Full code review, development |
| `pro` | User-defined | User-defined | Production, tuned budgets |
| `ai` | 6000 (capped) | ref | LLM context with query ranking |
| `fast` | n/a | off | Tree + manifest only, ultra-light |

### Token Budget Control
- `--budget-tokens NUM` - Total token budget for all files
- `--max-file-tokens NUM` - Per-file token limit
- `--sample-mode [off|ref|inline]` - Content sampling strategy

### File Filtering
- `--include-glob PATTERN` - Include files matching glob pattern
- `--exclude-glob PATTERN` - Exclude files matching glob pattern
- `--only-ext EXT1,EXT2` - Only process specified extensions
- `--exclude-ext EXT1,EXT2` - Exclude specified extensions

### Security & Masking
- `--masking [off|basic|advanced]` - Secret masking level
- `--mask-pattern REGEX` - Add custom masking regex pattern
- `--mask-pattern-file FILE` - Load patterns from file (file:// URI)

### AI/LLM Optimization
- `--ai-mode` - Enable LLM-optimized defaults
- `--query TEXT` - Rank files by semantic relevance to query

### Risk Analysis (Spicy)
- `--spicy / --no-spicy` - Enable/disable risk report (default: enabled)
- `--spicy-strict` - Exit with code 2 on high/critical findings

### Utilities
- `--dry-run` - Preview configuration without writing files
- `--verbose` - Increase output verbosity
- `--version` - Show version information
- `--help` - Display help message

## Configuration File

Create `pyproject.toml` in your project root:

```toml
[tool.dir2md]
preset = "pro"
include_glob = ["src/**/*.py", "tests/**/*.py"]
exclude_glob = ["**/__pycache__/**", "**/.venv/**"]
emit_manifest = true
budget_tokens = 8000

[tool.dir2md.masking]
patterns = ["(?i)secret_key\\s*=\\s*['\"]?[A-Za-z0-9]{16,}"]
pattern_files = ["file://./.dir2md/patterns.txt"]
```

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Security violation (with `--spicy-strict`)

## Examples

### Basic Usage
```bash
# Generate blueprint for current directory
dir2md .

# Specify output path
dir2md ./my-project -o blueprint.md
```

### AI/LLM Context
```bash
# Claude/Copilot optimized
dir2md . --ai-mode --query "authentication" --output-format jsonl

# Gemini optimized with manifest
dir2md . --ai-mode --emit-manifest --budget-tokens 4000
```

### Security Audit
```bash
# Basic masking
dir2md . --masking basic --spicy

# Strict mode (fail on high/critical)
dir2md . --masking advanced --spicy-strict
```

### CI/CD Integration
```bash
# Deterministic output
dir2md . --preset pro --emit-manifest --no-timestamp -o BLUEPRINT.md

# Quick validation
dir2md . --preset fast --dry-run
```

### Custom Filtering
```bash
# Python files only
dir2md . --only-ext py --budget-tokens 5000

# Exclude build artifacts
dir2md . --exclude-glob "**/dist/**" --exclude-glob "**/.venv/**"
```

### Docker
```bash
# Windows
docker run --rm -v %cd%:/work dir2md:local /work --ai-mode

# Linux/macOS
docker run --rm -v $PWD:/work dir2md:local /work --ai-mode
```

## Pattern File Format

JSON format for `--mask-pattern-file`:
```json
[
  "(?i)stripe_key\\s*=\\s*['\"]?sk_live_\\w+",
  "(?i)auth_token\\s*:\\s*['\"]?[A-Za-z0-9_-]{20,}",
  "custom_pattern_here"
]
```

Text format (one pattern per line):
```
(?i)secret_key\s*=\s*['"]?[A-Za-z0-9]{16,}
(?i)api_key\s*:\s*['"]?\w{32,}
```
