# Documentation Integration Plan

## Current Structure Analysis

### Existing Documents
1. **README.md** (root) - Professional landing page, 117 lines
2. **Wiki.md** (docs/) - Casual quick-start, developer-friendly
3. **CLI_REFERENCE.md** (docs/) - Complete CLI documentation
4. **FEATURES.md** (docs/) - Technical deep-dive
5. **TROUBLESHOOTING.md** (docs/) - Problem-solving guide

## Recommended Integration Strategy

### Option A: Wiki as Quick Start Hub (RECOMMENDED)

**Rationale:**
- Wiki.md has casual, approachable tone
- Serves as bridge between README and detailed docs
- Natural place for "getting started" content

**Implementation:**
```
README.md (root)
├─> Quick Start section links to Wiki.md
└─> Documentation section links to detailed docs

Wiki.md (docs/)
├─> "Learn More" section links to:
│   ├─> CLI_REFERENCE.md (complete options)
│   ├─> FEATURES.md (technical details)
│   └─> TROUBLESHOOTING.md (common issues)
└─> Keeps casual, example-focused style

CLI_REFERENCE.md - Complete reference
FEATURES.md - Technical specifications
TROUBLESHOOTING.md - Solutions guide
```

**Changes Needed:**
1. Add navigation section to Wiki.md (bottom)
2. Update README to link Wiki.md in Quick Start
3. Cross-link all docs for easy navigation

### Option B: Rename Wiki to QUICK_START

**Rationale:**
- More conventional naming
- Clearer purpose indication
- Better SEO/discoverability

**Implementation:**
```
docs/
├── QUICK_START.md (was Wiki.md) - Getting started fast
├── CLI_REFERENCE.md - Full command reference
├── FEATURES.md - Capabilities & architecture
└── TROUBLESHOOTING.md - Problem solving
```

**Changes Needed:**
1. Rename Wiki.md → QUICK_START.md
2. Update all links
3. Add navigation footer

### Option C: Merge Wiki into README

**Rationale:**
- Single entry point
- Less file navigation
- Common GitHub pattern

**Cons:**
- README becomes longer
- Less specialized documentation
- **NOT RECOMMENDED** (conflicts with goal of keeping README clean)

## Recommended Actions

### Phase 1: Enhance Wiki.md with Navigation
```markdown
## Learn More

### Complete Documentation
- **[CLI Reference](CLI_REFERENCE.md)** - All commands and options
- **[Features Guide](FEATURES.md)** - Technical capabilities and architecture
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

### Community
- [GitHub Issues](https://github.com/Flamehaven/dir2md/issues)
- [Discussions](https://github.com/Flamehaven/dir2md/discussions)
```

### Phase 2: Update README Quick Start
```markdown
## Quick Start

For a quick introduction, see **[Wiki.md](docs/Wiki.md)** — developer-friendly guide with examples.

For complete documentation, visit the **[docs/](docs/)** folder.
```

### Phase 3: Add Navigation to All Docs
Footer template for all doc files:
```markdown
---

**Navigation:** [README](../README.md) | [Quick Start](Wiki.md) | [CLI Reference](CLI_REFERENCE.md) | [Features](FEATURES.md) | [Troubleshooting](TROUBLESHOOTING.md)
```

## Content Gaps to Fill

### Missing Documentation
1. **API Documentation** (if library usage exists)
2. **Architecture Diagram** (for FEATURES.md)
3. **Migration Guide** (if from other tools)
4. **Performance Benchmarks** (for FEATURES.md)
5. **Security Best Practices** (expand masking guide)

### Wiki.md Enhancement Opportunities
- Add animated GIF/screenshots of output
- Include "Before/After" examples
- Add common patterns (Django, React, etc.)
- Link to video tutorial (if exists)

## Maintenance Strategy

### Documentation Owner Workflow
1. **README.md** - High-level only, link to details
2. **Wiki.md** - Keep casual and example-focused
3. **CLI_REFERENCE.md** - Generated from `--help` (automate?)
4. **FEATURES.md** - Update with new features
5. **TROUBLESHOOTING.md** - Add community-reported issues

### Version Control
- Tag docs with version numbers for breaking changes
- Maintain CHANGELOG.md in sync
- Archive old docs in `docs/archive/v1.x/`

## Success Metrics

- [ ] All docs cross-linked
- [ ] No orphan documentation
- [ ] Clear navigation path from README → specific topics
- [ ] Casual (Wiki) + Technical (FEATURES) + Reference (CLI) balance
- [ ] Under 3 clicks to any information

## Timeline

**Immediate** (< 1 hour):
- Add navigation to Wiki.md
- Update README Quick Start link
- Cross-link existing docs

**Short-term** (this week):
- Consider Wiki → QUICK_START rename
- Add screenshots/examples
- Fill content gaps

**Long-term** (ongoing):
- Automate CLI reference from code
- Add video tutorials
- Collect FAQ from issues
