import re
from typing import Iterable, Dict, Pattern

# Guard extremely large inputs from expensive regex processing (ReDoS safety)
MAX_MASK_INPUT_CHARS = 1_000_000
MAX_MASK_CHUNK_OVERLAP = 256

# Basic masking rules (available in OSS version)
BASIC_MASKING_RULES = {
    "AWS_ACCESS_KEY_ID": r"AKIA[0-9A-Z]{16}",
    "BEARER_TOKEN": r"[Bb]earer\s+[A-Za-z0-9\-\._~\+\/]+=*",
    "PRIVATE_KEY": r"-----BEGIN ((EC|RSA|OPENSSH) )?PRIVATE KEY-----.*?-----END ((EC|RSA|OPENSSH) )?PRIVATE KEY-----",
    "GENERIC_API_KEY": r"(?i)(api[_-]?key|x-api-key|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{20,64}['\"]?",
    "DATABASE_URL": r"(?i)(postgres|mysql|mariadb|mongodb(\+srv)?|sqlserver|redis)://[^\s]+",
    "JWT_TOKEN": r"[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]{16,}",
    "OAUTH_CLIENT_SECRET": r"(?i)(client[_-]?secret)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,64}['\"]?",
}

# Advanced masking rules (now also available in OSS)
ADVANCED_MASKING_RULES = {
    "AWS_SECRET_ACCESS_KEY": r"(?i)aws_secret_access_key\s*=\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
    "GENERIC_API_KEY": r"(?i)api[_-]?key\s*=\s*['\"]?[A-Za-z0-9_.-]{32,45}['\"]?",
    "SLACK_TOKEN": r"xox[p|b|o|a]-[0-9]{12}-[0-9]{12}-[0-9]{12}-[a-z0-9]{32}",
    "GITHUB_TOKEN": r"ghp_[0-9a-zA-Z]{36}",
    "GITHUB_PAT": r"gh[pousr]_[0-9A-Za-z]{36}",
    # Pro version would have many more patterns
    "AZURE_KEY": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    "GCP_KEY": r"(?i)google[_-]?api[_-]?key\s*=\s*['\"]?[A-Za-z0-9_.-]{39}['\"]?",
}

MASK_REPLACEMENT = "[*** MASKED_SECRET ***]"
PRO_MASK_REPLACEMENT = "[*** MASKED_SECRET_PRO ***]"
CUSTOM_MASK_REPLACEMENT = "[*** MASKED_SECRET ***]"

# Pre-compiled regex cache for faster and safer masking
_COMPILED_RULES: Dict[str, Dict[str, Pattern[str]]] = {"basic": {}, "advanced": {}}


def _compile_rules() -> None:
    """Compile masking regex patterns at import time."""
    for name, pattern in BASIC_MASKING_RULES.items():
        flags = re.DOTALL if name == "PRIVATE_KEY" else 0
        _COMPILED_RULES["basic"][name] = re.compile(pattern, flags=flags)

    _COMPILED_RULES["advanced"].update(_COMPILED_RULES["basic"])
    for name, pattern in ADVANCED_MASKING_RULES.items():
        _COMPILED_RULES["advanced"][name] = re.compile(pattern)


_compile_rules()


def get_active_masking_rules(mode: str = "basic") -> dict[str, Pattern[str]]:   
    """Return compiled masking rules for the requested mode."""
    if mode == "advanced":
        return _COMPILED_RULES["advanced"]
    return _COMPILED_RULES["basic"]


def _length_preserving_replace(match: re.Match, replacement: str) -> str:
    matched = match.group(0)
    if not matched:
        return replacement
    if len(replacement) >= len(matched):
        return replacement[: len(matched)]
    return replacement + ("*" * (len(matched) - len(replacement)))


def _apply_masking_rules(
    text: str,
    rules: dict[str, Pattern[str]],
    custom_patterns: Iterable[str] | None,
    length_preserving: bool,
) -> str:
    # Apply custom patterns first so project-specific rules run before bundled ones.
    if custom_patterns:
        for pattern in custom_patterns:
            try:
                compiled = re.compile(pattern, flags=re.DOTALL)
                if length_preserving:
                    text = compiled.sub(
                        lambda m: _length_preserving_replace(m, CUSTOM_MASK_REPLACEMENT),
                        text,
                    )
                else:
                    text = compiled.sub(CUSTOM_MASK_REPLACEMENT, text)
            except re.error as exc:
                print(f"[WARN] Skipping invalid custom mask pattern: {pattern!r} ({exc})")

    for rule_name, pattern in rules.items():
        replacement = PRO_MASK_REPLACEMENT if rule_name in ADVANCED_MASKING_RULES else MASK_REPLACEMENT
        if length_preserving:
            text = pattern.sub(lambda m: _length_preserving_replace(m, replacement), text)
        else:
            text = pattern.sub(replacement, text)
    return text


def _mask_large_text(
    text: str,
    rules: dict[str, Pattern[str]],
    custom_patterns: Iterable[str] | None,
) -> str:
    if not rules and not custom_patterns:
        return text
    chunk_size = MAX_MASK_INPUT_CHARS
    overlap = min(MAX_MASK_CHUNK_OVERLAP, max(0, chunk_size // 10))
    out_parts: list[str] = []
    text_len = len(text)
    start = 0
    while start < text_len:
        end = min(start + chunk_size, text_len)
        window_start = max(0, start - overlap)
        window_end = min(text_len, end + overlap)
        window = text[window_start:window_end]
        masked = _apply_masking_rules(window, rules, custom_patterns, length_preserving=True)
        slice_start = start - window_start
        slice_end = slice_start + (end - start)
        out_parts.append(masked[slice_start:slice_end])
        start = end
    return "".join(out_parts)


def apply_masking(text: str, mode: str = "basic", custom_patterns: Iterable[str] | None = None) -> str:
    """Apply masking rules with optional custom patterns (no license gating)."""

    if not text:
        return text

    if mode == "off":
        rules: dict[str, Pattern[str]] = {}
    else:
        rules = get_active_masking_rules(mode)

    # Anti-ReDoS: chunk large payloads but still mask (length-preserving).
    if len(text) > MAX_MASK_INPUT_CHARS:
        return _mask_large_text(text, rules, custom_patterns)

    return _apply_masking_rules(text, rules, custom_patterns, length_preserving=False)
