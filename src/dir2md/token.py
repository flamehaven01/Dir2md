from __future__ import annotations

import math
from functools import lru_cache


@lru_cache(maxsize=2048)
def estimate_tokens(text: str) -> int:
    """Estimate token count using a rough 4 chars-per-token heuristic."""
    if not text:
        return 1
    return max(1, math.ceil(len(text) / 4))
