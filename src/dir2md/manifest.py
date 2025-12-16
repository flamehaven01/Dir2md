"""Manifest helpers for dir2md."""
from pathlib import Path
import json
import hashlib

def sha256_bytes(b: bytes) -> str:
    """Compute SHA256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()

def sha256_string(text: str) -> str:
    """Compute SHA256 hash of string (UTF-8 encoded)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    """Compute SHA256 hash of file contents.

    Reads file in chunks to handle large files efficiently.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(data: dict, out: Path) -> None:
    """Write a JSON manifest to disk."""
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
