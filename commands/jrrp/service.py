"""Daily luck (今日人品 / JRRP) calculation service.

Platform-agnostic deterministic daily pseudo-random generator.
Score is derived solely from user_id + date; no persistence required.
"""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Final

# Bump this when the algorithm changes so old results remain reproducible
# under their original version if needed in the future.
ALGORITHM_VERSION: Final[int] = 1


def djb2_hash(value: str) -> int:
    """Standard DJB2 hash, 31-bit positive result for stable seeding.

    Uses character ordinals (Unicode code points) so the result is
    independent of Python's runtime hash randomisation.
    """
    hash_value = 5381
    for char in value:
        hash_value = ((hash_value * 33) + ord(char)) & 0xFFFFFFFF
    return hash_value & 0x7FFFFFFF


def _xorshift32(seed: int) -> int:
    """Simple 32-bit xorshift PRNG step. Deterministic across platforms."""
    seed &= 0xFFFFFFFF
    seed ^= (seed << 13) & 0xFFFFFFFF
    seed ^= (seed >> 17) & 0xFFFFFFFF
    seed ^= (seed << 5) & 0xFFFFFFFF
    return seed & 0xFFFFFFFF


def generate_identifier(user_id: str) -> str:
    """Produce a stable, display-only identifier for a user.

    Algorithm:
        UTF-8(user_id) → SHA-512 hex → characters 65-80 (1-based)
        → format as XXXX-XXXX-XXXX-XXXX
    """
    digest = hashlib.sha512(user_id.encode("utf-8")).hexdigest()
    # 1-based positions 65-80 → 0-based slice [64:80]
    part = digest[64:80]
    return "-".join(
        [
            part[0:4],
            part[4:8],
            part[8:12],
            part[12:16],
        ]
    ).upper()


def calculate_daily_luck(user_id: str, on_date: date) -> int:
    """Return a deterministic daily luck score in [0, 100].

    Same (user_id, date) always yields the same score.
    Different dates or users generally yield different scores.
    """
    seed_text = f"v{ALGORITHM_VERSION}:{user_id}{on_date:%Y%m%d}"
    seed = djb2_hash(seed_text)
    # Ensure non-zero seed for xorshift
    if seed == 0:
        seed = 1
    raw = _xorshift32(seed)
    return raw % 101


def luck_level(score: int) -> str:
    """Optional human-readable level for UI (not part of the core algorithm)."""
    if score >= 100:
        return "今日人品爆棚"
    if score >= 90:
        return "极佳"
    if score >= 70:
        return "不错"
    if score >= 50:
        return "尚可"
    if score >= 30:
        return "一般"
    if score >= 10:
        return "较差"
    return "极差"
