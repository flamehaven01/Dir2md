# Contributing to dir2md

We welcome contributions! Please follow these guidelines to keep changes smooth and reviewable.

## Development Setup
```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run tests before sending changes:
```bash
python -m pytest tests
```

Optional lint (when we enable it in CI):
```bash
python -m pylint src/dir2md
```

## Branching and Commits
- Use a feature branch from `main`.
- Commit messages: short and imperative (e.g., “Add spicy strict exit”).
- Keep changes focused; separate unrelated fixes.

## Pull Requests
- Describe the change, motivation, and behavior impact.
- Note any CLI/flag changes and update README/CHANGELOG when relevant.
- Include test commands you ran.
- Artifacts: if your change affects output, attach a sample md/json/jsonl.

## Releases
- Version bumps are handled in PRs; CHANGELOG must be updated.
- GitHub Actions `Release` workflow can publish to PyPI/TestPyPI (requires secrets).

## Coding Style
- Python 3.10+
- Keep CLI messages ASCII-safe.
- Default outputs aim to serve both humans (md) and LLMs (jsonl); avoid breaking these defaults.

Thanks for helping make dir2md better! If you have questions, reach us at info@flamehaven.space.
