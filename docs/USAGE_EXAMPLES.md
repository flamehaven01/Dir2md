# Usage Examples

Quick, copy-pasteable recipes for common dir2md tasks.

## Generate a dual blueprint (md + jsonl)
```bash
dir2md . --ai-mode --spicy
```

## Ultra-light context (tree + manifest only)
```bash
dir2md . --fast
```

## Query-focused context for LLMs
```bash
dir2md . --ai-mode --query "auth flow" --output-format jsonl
```

## Security-conscious run (masking on)
```bash
dir2md . --masking basic --emit-manifest --no-timestamp
```

## CI-friendly deterministic output path
```bash
dir2md . --output PROJECT_BLUEPRINT.md --emit-manifest --no-timestamp
```
