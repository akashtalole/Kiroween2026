"""Deterministic autonomy policy: any signal can raise the tier, none can lower it."""
from dataclasses import dataclass, field
from fnmatch import fnmatch

TIERS = ["A0", "A1", "A2", "A3"]  # A0 = safest

A3_PATHS = ["**/auth/**", "**/secrets/**", "infra/**", "**/migrations/**"]
A0_PATHS = ["docs/**", "**/*.md", "tests/**", "**/test_*.py"]

@dataclass(frozen=True)
class Change:
    paths: tuple = ()
    diff_lines: int = 0
    public_api_changed: bool = False
    deps_changed: bool = False
    gates_passed: bool = True
    reviews_passed: int = 2

def _rank(tier: str) -> int:
    return TIERS.index(tier)

def classify(c: Change) -> str:
    rank = 0
    for p in c.paths:
        if any(fnmatch(p, g) for g in A3_PATHS):
            rank = max(rank, 3)
        elif any(fnmatch(p, g) for g in A0_PATHS):
            rank = max(rank, 0)
        else:
            rank = max(rank, 1)          # ordinary source code
    if c.diff_lines > 250:
        rank = max(rank, 2)
    if c.public_api_changed or c.deps_changed:
        rank = max(rank, 2)
    return TIERS[rank]

def decide(c: Change) -> str:
    if not c.gates_passed:
        return "reject"
    tier = classify(c)
    if tier in ("A2", "A3"):
        return "queue_for_human"
    if tier == "A1" and c.reviews_passed < 2:
        return "queue_for_human"
    return "merge"
