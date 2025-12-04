# Features Documentation

Complete feature reference for Dir2md.

**Quick Start:** [Wiki.md](Wiki.md) | **Main:** [README](../README.md) | **CLI:** [CLI_REFERENCE.md](CLI_REFERENCE.md) | **Help:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Core Capabilities

### Smart Content Sampling
Dir2md intelligently samples large files to fit within token budgets while preserving context.

**Sampling Modes:**
- `off` - No sampling, include full content
- `ref` - Generate file references only (tree structure)
- `inline` - Head/tail sampling with configurable limits

**How it works:**
- Analyzes file sizes and token counts
- Prioritizes important sections (imports, exports, main functions)
- Maintains code structure visibility
- Preserves context with head/tail sampling

### Security Masking

Automatic detection and masking of sensitive information.

**Built-in Pattern Categories:**
- **PEM Blocks**: RSA keys, certificates, private keys
- **API Keys**: AWS, Stripe, SendGrid, Twilio
- **Tokens**: GitHub, GitLab, Bearer tokens
- **Credentials**: Database URLs, passwords, connection strings
- **JWTs**: JSON Web Tokens
- **OAuth**: Client secrets, refresh tokens

**Masking Levels:**
- `off` - No masking
- `basic` - Common patterns (API keys, tokens, PEM blocks)
- `advanced` - Extended patterns including database URLs, JWTs

**Custom Patterns:**
```bash
# Single pattern
dir2md . --masking basic --mask-pattern "(?i)custom_secret_\w+"

# Pattern file
dir2md . --masking basic --mask-pattern-file file:///path/to/patterns.json
```

### Duplicate Detection

SimHash-based content deduplication prevents redundant information in output.

**Benefits:**
- Reduces token usage
- Eliminates repeated boilerplate
- Maintains unique code blocks
- Configurable similarity threshold

**How it works:**
- Generates content fingerprints
- Compares across files
- Marks duplicates with reference links
- Preserves one canonical version

### Token Budget Management

Fine-grained control over output size for LLM context windows.

**Budget Controls:**
- `--budget-tokens` - Total budget for all files
- `--max-file-tokens` - Per-file limit
- Automatic distribution across files
- Priority-based allocation

**Smart Allocation:**
- Important files get larger share
- Query-matched files prioritized
- Small files included whole
- Large files sampled efficiently

## Output Formats

### Markdown (.md)
Human-readable blueprint with structure and samples.

**Contents:**
- Directory tree visualization
- File metadata (size, tokens, line count)
- Code samples with syntax highlighting
- Risk findings (if spicy enabled)
- Masked secrets indicators

### JSONL (.jsonl)
Line-delimited JSON for AI/LLM ingestion.

**Structure:**
```jsonl
{"type": "file", "path": "src/main.py", "content": "...", "meta": {...}}
{"type": "file", "path": "tests/test.py", "content": "...", "meta": {...}}
```

**Benefits:**
- Streaming-friendly
- Easy to parse
- Preserves metadata
- LLM-optimized

### JSON (.json)
Structured JSON with full metadata.

**Structure:**
```json
{
  "tree": {...},
  "files": [...],
  "manifest": {...},
  "spicy": {...}
}
```

### Manifest (.manifest.json)
Metadata-only output without file content.

**Contents:**
- File statistics
- Token counts
- Directory structure
- Risk assessment summary
- Generation metadata

## AI/LLM Optimization

### AI Mode
Preset configuration optimized for LLM context windows.

**Enabled with:** `--ai-mode`

**Includes:**
- 6000 token budget (Claude/GPT optimized)
- Automatic JSONL generation
- Query ranking enabled
- Smart sampling
- Security masking

### Semantic Query Ranking
Rank and filter files by relevance to a natural language query.

**Usage:**
```bash
dir2md . --ai-mode --query "authentication flow"
dir2md . --ai-mode --query "database migration logic"
```

**How it works:**
- Analyzes file content semantically
- Scores relevance to query
- Reorders files by match quality
- Includes top matches within budget
- Shows relevance scores in output

## Risk Analysis (Spicy)

Security-focused code analysis with severity-based findings.

### Severity Levels
- `ok` - No issues detected
- `warn` - Minor concerns (TODO, deprecated patterns)
- `risk` - Moderate risks (weak crypto, eval usage)
- `high` - Serious vulnerabilities (hardcoded secrets visible)
- `critical` - Severe security issues (exposed credentials)

### Detection Categories
- **Secrets**: Hardcoded API keys, passwords, tokens
- **Crypto**: Weak algorithms, insecure configurations
- **Injection**: SQL, command, code injection risks
- **Access Control**: Insecure permissions, authentication gaps
- **Data Exposure**: Sensitive data in logs, debug output

### Strict Mode
Fail build/CI on high/critical findings.

```bash
dir2md . --spicy-strict
# Exit code 2 if high/critical found
# Exit code 0 if only warn/risk
```

### Output Integration
- **Markdown**: Dedicated spicy section with findings
- **JSON/JSONL**: `spicy.score`, `spicy.counts`, `spicy.findings[]`
- **Manifest**: Summary statistics only

## Configuration System

### Preset Profiles

**Raw Preset**
```toml
[tool.dir2md.preset.raw]
budget_tokens = null  # Unlimited
sample_mode = "inline"
emit_manifest = false
```

**Pro Preset**
```toml
[tool.dir2md.preset.pro]
budget_tokens = null  # User-defined
sample_mode = null    # User-defined
emit_manifest = true
```

**AI Preset**
```toml
[tool.dir2md.preset.ai]
budget_tokens = 6000
sample_mode = "ref"
emit_manifest = true
masking = "basic"
```

**Fast Preset**
```toml
[tool.dir2md.preset.fast]
budget_tokens = 0
sample_mode = "off"
emit_manifest = true
```

### File-Based Config

**pyproject.toml Example:**
```toml
[tool.dir2md]
preset = "pro"
budget_tokens = 8000
max_file_tokens = 500
include_glob = ["src/**/*.py", "tests/**/*.py"]
exclude_glob = ["**/__pycache__/**"]
emit_manifest = true
ai_mode = false

[tool.dir2md.masking]
level = "basic"
patterns = [
    "(?i)custom_secret_\\w+",
    "(?i)internal_token\\s*=\\s*['\"]?\\w+"
]
pattern_files = ["file://./.dir2md/patterns.txt"]

[tool.dir2md.spicy]
enabled = true
strict = false
```

## Integration Features

### CI/CD Support
- Deterministic output (`--no-timestamp`)
- Exit codes for automation
- Dry-run mode for validation
- Configurable output paths

### Docker Support
Pre-built container for consistent execution across environments.

```dockerfile
FROM python:3.9-slim
COPY . /app
RUN pip install -e /app
ENTRYPOINT ["python", "-m", "src.dir2md.cli"]
```

### Git Integration
- Respects `.gitignore` patterns
- Detects repository metadata
- Branch and commit info in manifest

## Performance Optimizations

### Parallel Processing
- Concurrent file reading
- Parallel content analysis
- Async I/O operations

### Memory Efficiency
- Streaming file processing
- Lazy content loading
- Incremental token counting

### Cache System
- File hash caching
- Pattern compilation cache
- Metadata persistence

## SIDRCE Certification

**Certification Details:**
- **ID**: SIDRCE-DIR2MD-20251203-ARCHON
- **Scores**: 
  - Integrity: 98/100
  - Resonance: 95/100
  - Stability: 95/100
  - Overall: 96/100 (Certified)

**Architecture Principles:**
- Distributed responsibilities (walker, selector, renderer, orchestrator)
- No god-object anti-patterns
- Clear separation of concerns
- Comprehensive test coverage

**Quality Standards:**
- Deterministic pytest behavior
- Cross-platform compatibility
- Production-ready error handling
- Security-first design
