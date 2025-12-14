# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.3] - 2025-12-14

### Added
- **Phantom Code Detection**: Automatically detects dead code analysis tools in the system path.
  - Reports unused code/imports as **CRITICAL** "Phantom" findings.
  - Helps keep codebases clean by identifying structural atrophy.

## [1.1.2] - 2025-12-09

### Security
- Masking now pre-compiles basic/advanced regexes and skips processing when input exceeds a safe threshold to reduce ReDoS risk.
- Large individual files are skipped before read when they exceed 1MB, preventing OOM/hangs while still noting the skip.

### Performance
- Token estimation is cached with LRU (maxsize 2048) and keeps a minimum of one token for empty strings.

### Behavior/UX
- Skipped oversized files now record placeholder hash/summary so the skip is visible in outputs and manifests.
- Custom masking patterns are compiled before use; invalid patterns emit warnings and are ignored.

### Tests
- Pytest suite: 22 passed, 2 skipped.

## [1.1.1] - 2025-12-04

### Removed
- Pro/license gating entirely: deleted `license.py`, removed license checks from masking/parallel/CLI/tests; `.env.example` no longer includes license keys.
- Blueprint workflow retired; CI now runs ruff + pytest only.

### Fixed
- HF demo import path includes `src` so `dir2md` imports resolve in Spaces.
- Lint/test cleanup after refactor (ruff + pytest green).
- Default excludes now drop cache/venv noise (`.pytest_cache_local`, `.ruff_cache`, `venv_clean`) for cleaner blueprints out of the box.
- Spicy is now enabled by default; `--no-spicy` disables, `--spicy-strict` enforces failure on high/critical.

### Documentation
- Updated README/demo metadata (Spicy branding, HF front matter); pending: scrub remaining Pro/license mentions in docs.

## [1.1.0] - 2025-12-02

### Added
- AI-friendly query & output:
  - `--query` filters/sorts files by match score and injects snippets.
  - `--output-format md|json|jsonl` for LLM/CLI pipelines.
- Simplified presets with new flags:
  - `--ai-mode` (ref mode, capped budgets, stats/manifest on).
  - `--fast` (tree + manifest only; contents skipped).
- Spicy risk report:
  - `--spicy` adds severity counts/score/findings to md/json/jsonl/manifest.
  - `--spicy-strict` exits non-zero when high/critical findings are present.
- CLI polish: `[INFO]` status, `--progress` verbosity selector, plan summary line.
- Safety/performance hardening: symlink escape guard, streaming file read with full hash, manifest reuse.
- Packaging and release:
  - Default output now md + jsonl for human + LLM use.
  - Added GitHub Actions Release workflow (PyPI/TestPyPI publish).
  - Docker usage documented; existing Dockerfile installs package.
- Architecture decoupling: introduced `walker.py`, `selector.py`, `renderer.py`, and `orchestrator.py` to reduce the `core.py` god-object risk.
- Tests expanded beyond the monolith: added module coverage for masking, search, token, spicy, and CLI defaults.

### Changed
- Default preset remains `pro`; `iceberg` references removed from docs.

### Fixed
- `fast` mode now skips file content reads.
- Plan summary reflects post-preset effective settings.
- Fixed `--include-glob`/`--exclude-glob` NameError when compiling pathspecs.

### Tests
- Expanded pytest coverage for symlinks, streaming hashes, query filtering/snippets, JSONL output, masking, spicy, search, and token logic (22 passed, 2 skipped).

## [1.0.4] - 2025-10-09

### Added

#### Enhanced Security Masking
- Expanded default masking coverage to include GitHub personal access tokens, generic API keys, database URLs, JWTs, and OAuth client secrets in the open source build
- New patterns detected:
  - GitHub Personal Access Tokens: `ghp_*`, `gho_*`, `ghu_*`, `ghs_*`, `ghr_*`
  - Generic API Keys: `api_key=`, `apikey=`, `api-key=`
  - Database URLs: PostgreSQL, MySQL, MongoDB connection strings
  - JSON Web Tokens (JWTs): `eyJ*` base64-encoded tokens
  - OAuth Client Secrets: `client_secret=`, `oauth_secret=`

#### Automatic Environment Configuration
- Automatically load the nearest `.env` file when launching the CLI so license keys and shared defaults are available without manual exports
- Zero-configuration startup for teams using `.env` files
- Seamless Pro license activation

#### User-Defined Masking Patterns
- Support user-defined masking patterns via `--mask-pattern` flags, `--mask-pattern-file` for loading from files, and `[tool.dir2md.masking]` configuration in `pyproject.toml`
- Three flexible methods:
  1. Inline patterns: `--mask-pattern "regex"`
  2. Pattern files: JSON arrays or newline-delimited text via `file://` URIs
  3. Configuration: `[tool.dir2md.masking]` section in `pyproject.toml`

### Changed

#### Expanded Default Exclusions
- Extended the default exclusion set to skip common secret-bearing files such as `.env*`, certificate bundles, and private key formats before scanning directories
- New exclusions: `.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `*.crt`, `*.cer`, `*.der`

#### Windows Compatibility Improvements
- Sanitized the public documentation to use ASCII-only characters for Windows cp949 compatibility
- ASCII-safe replacements: `[#]`, `[!]`, `[+]`, `[*]`, `[T]` instead of emojis
- Prevents `illegal multibyte sequence` errors on Windows systems

#### Documentation Clarity
- Clarified relationship with IsaacBreen's `dir2md` (PyPI package)
- Added **Acknowledgments** section for community transparency
- Updated installation instructions to reflect GitHub-only distribution
- Removed "coming soon" language for PyPI availability

### Fixed

#### [CRITICAL] Windows file:// URI Parsing Error
- **Issue:** Windows `file://` URI handling for pattern files failed with `"Invalid argument: '\C:...'"` error due to incorrect path slicing
- **Root cause:** Path parsing didn't account for Windows absolute paths (`C:\...`)
- **Solution:** Properly strips leading slash for Windows absolute paths (`file:///C:/path` → `C:/path`)
- **Impact:** Custom masking pattern files now work correctly on Windows systems

#### [SECURITY] GitHub PAT Pattern Misplacement
- **Issue:** GitHub Personal Access Token pattern (`gh[pousr]_[0-9A-Za-z]{36}`) was incorrectly placed in basic masking rules instead of advanced (Pro-only)
- **Risk:** Open-source users received Pro-level pattern matching without license validation
- **Solution:** Moved GitHub PAT pattern to advanced masking rules, enforcing proper Pro license requirement
- **Impact:** Correct separation between OSS basic and Pro advanced masking tiers

#### Advanced Masking Notice Deduplication
- Ensure the advanced masking upgrade notice prints only once per session when advanced mode is requested without an active Pro license
- **Before:** Multiple notices during single CLI run
- **After:** Single notice at first invocation

### Testing

#### Automated Tests
- 12 tests passing (1 skipped for symlinks on systems without support)
- Full `pytest` suite coverage for core functionality
- Regression tests for Windows `file://` URI paths

#### Manual Verification
- Custom masking patterns load correctly from JSON files
- Custom masking patterns load correctly from text files
- Windows `file://` URI paths resolve properly (`file:///C:/...`)
- Basic vs advanced masking mode separation enforced
