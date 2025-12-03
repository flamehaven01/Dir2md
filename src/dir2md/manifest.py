from __future__ import annotations
"""Manifest helpers for dir2md."""
from pathlib import Path
import json
import hashlib

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def write_manifest(data: dict, out: Path) -> None:
    """Write a JSON manifest to disk."""
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
