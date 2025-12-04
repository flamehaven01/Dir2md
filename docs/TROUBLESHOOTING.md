# Troubleshooting Guide

Common issues and solutions for Dir2md.

**Quick Start:** [Wiki.md](Wiki.md) | **Main:** [README](../README.md) | **CLI:** [CLI_REFERENCE.md](CLI_REFERENCE.md) | **Features:** [FEATURES.md](FEATURES.md)

## Installation Issues

### Package Not Found
```bash
# Error: No matching distribution found for dir2md
# Fix: Use GitHub installation
git clone https://github.com/Flamehaven/dir2md.git
cd dir2md
pip install -e .
```

### Dependency Conflicts
```bash
# Error: Cannot install conflicting dependencies
# Fix: Use virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
pip install -e .
```

## Runtime Errors

### File Encoding Issues
```bash
# Error: UnicodeDecodeError or cp949 codec errors
# Fix 1: Exclude problematic files
dir2md . --exclude-glob "**/*.bin" --exclude-glob "**/*.dat"

# Fix 2: Specify file types explicitly
dir2md . --only-ext "py,js,md,txt"
```

### Pattern File Not Loading (Windows)
```bash
# Error: [WARN] Could not read mask pattern file
# Cause: Incorrect file:// URI format
# Fix: Use triple slash for absolute paths
dir2md . --mask-pattern-file file:///C:/path/to/patterns.json

# Relative path
dir2md . --mask-pattern-file file://./patterns.json
```

### Token Budget Exceeded
```bash
# Symptom: Output is truncated or incomplete
# Fix 1: Increase budget
dir2md . --budget-tokens 10000

# Fix 2: More aggressive filtering
dir2md . --budget-tokens 5000 --only-ext "py,js" --exclude-glob "**/tests/**"

# Fix 3: Use fast preset for overview
dir2md . --preset fast
```

### Manifest Not Generated
```bash
# Symptom: .manifest.json file missing
# Cause: raw preset disables manifests by default
# Fix: Use pro preset or enable explicitly
dir2md . --preset pro --emit-manifest
# Or
dir2md . --preset raw --emit-manifest
```

## Security & Masking Issues

### Secrets Still Visible
```bash
# Symptom: API keys or tokens not masked
# Fix 1: Enable masking
dir2md . --masking basic

# Fix 2: Test with dry-run first
dir2md . --masking basic --dry-run

# Fix 3: Add custom pattern
dir2md . --masking basic --mask-pattern "your_secret_pattern"

# Fix 4: Use advanced masking
dir2md . --masking advanced
```

### False Positive Masking
```bash
# Symptom: Legitimate code is masked incorrectly
# Cause: Overly broad masking patterns
# Fix: Use basic masking or customize patterns
dir2md . --masking basic
```

## Output Issues

### Empty Output File
```bash
# Symptom: Generated file exists but is nearly empty
# Cause 1: All files excluded by filters
# Fix: Check include/exclude patterns
dir2md . --verbose --dry-run

# Cause 2: Token budget too low
# Fix: Increase budget or remove limit
dir2md . --budget-tokens 10000
```

### Duplicate Content
```bash
# Symptom: Same code appears multiple times
# Cause: Deduplication disabled or threshold too low
# Fix: Enabled by default; if issues persist, report as bug
```

### Missing Files in Output
```bash
# Symptom: Expected files not included
# Fix 1: Check filters
dir2md . --verbose --dry-run

# Fix 2: Verify file extensions
dir2md . --only-ext "py,js,ts,tsx"

# Fix 3: Check .gitignore influence
# Dir2md respects .gitignore by default
```

## Docker Issues

### Volume Mount Errors
```bash
# Error: Cannot access /work directory
# Fix Windows: Use absolute path with drive letter
docker run --rm -v C:\path\to\project:/work dir2md:local /work

# Fix Linux/macOS: Ensure proper permissions
docker run --rm -v $(pwd):/work dir2md:local /work
```

### Build Failures
```bash
# Error: Docker build fails
# Fix 1: Update Docker
# Fix 2: Clean build
docker build --no-cache -t dir2md:local .

# Fix 3: Check Dockerfile for platform issues
```

## Performance Issues

### Very Slow Processing
```bash
# Symptom: Takes minutes on small projects
# Cause: Processing large binary files or many files
# Fix 1: Exclude binaries
dir2md . --exclude-glob "**/*.{jpg,png,gif,pdf,zip}"

# Fix 2: Use fast preset
dir2md . --preset fast

# Fix 3: Limit file types
dir2md . --only-ext "py,js,ts"
```

### High Memory Usage
```bash
# Symptom: Out of memory errors
# Cause: Very large codebase with unlimited budget
# Fix: Set reasonable token budget
dir2md . --budget-tokens 8000 --max-file-tokens 500
```

## AI Integration Issues

### Context Too Large for LLM
```bash
# Symptom: LLM rejects input as too long
# Fix 1: Reduce budget
dir2md . --ai-mode --budget-tokens 4000

# Fix 2: Use query filtering
dir2md . --ai-mode --query "specific feature"

# Fix 3: Use fast preset for overview
dir2md . --preset fast
```

### Query Ranking Not Working
```bash
# Symptom: Query doesn't affect file ordering
# Cause: --ai-mode not enabled
# Fix: Must use --ai-mode with --query
dir2md . --ai-mode --query "authentication"
```

## Configuration Issues

### pyproject.toml Not Detected
```bash
# Symptom: Config file ignored
# Cause 1: File not in working directory
# Fix: Ensure pyproject.toml is in project root

# Cause 2: Syntax error in TOML
# Fix: Validate TOML syntax
python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))"
```

### CLI Flags Override Config
```bash
# Symptom: Config file settings ignored
# Cause: CLI flags take precedence (by design)
# Fix: Remove conflicting CLI flags or adjust config
```

## Getting Help

If your issue isn't covered here:

1. **Search existing issues**: [GitHub Issues](https://github.com/Flamehaven/dir2md/issues)
2. **Check discussions**: [GitHub Discussions](https://github.com/Flamehaven/dir2md/discussions)
3. **Create new issue**: Include:
   - Dir2md version (`dir2md --version`)
   - Python version (`python --version`)
   - Operating system
   - Full command used
   - Error message (if any)
   - Expected vs actual behavior
4. **Security issues**: Email info@flamehaven.space

## Debug Mode

For detailed troubleshooting information:
```bash
# Enable verbose output
dir2md . --verbose --dry-run

# Check what will be processed
dir2md . --dry-run

# Test specific features
dir2md . --masking basic --dry-run --verbose
```
