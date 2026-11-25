# Lab 05 · The autonomy policy engine and its property tests

**Goal:** the part that decides "may this merge without a human" must be deterministic code, and heavily tested. Experiment **E7** (planted bugs).

> **Tested:** the code and tests below live in `examples/policy-engine/` in the repo and pass (`5 passed`). Run them yourself:

```bash
pip install hypothesis pytest
cd examples/policy-engine && python -m pytest -q
```

## The engine

Escalation is **monotonic**: any single signal can raise the tier, none can lower it.

```python
"""Deterministic autonomy policy: any signal can raise the tier, none can lower it."""
from dataclasses import dataclass
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
```

## The properties

```python
from hypothesis import given, strategies as st
from policy import Change, classify, decide, _rank

paths = st.lists(st.sampled_from([
    "docs/a.md", "src/app.py", "tests/test_a.py", "src/auth/login.py",
    "infra/main.tf", "db/migrations/001.sql"]), max_size=6)
changes = st.builds(Change, paths=paths.map(tuple), diff_lines=st.integers(0, 2000),
                    public_api_changed=st.booleans(), deps_changed=st.booleans(),
                    gates_passed=st.booleans(), reviews_passed=st.integers(0, 2))

@given(changes, st.sampled_from(["src/new.py", "src/auth/x.py", "docs/x.md"]))
def test_adding_a_file_never_lowers_tier(c, extra):
    bigger = Change(c.paths + (extra,), c.diff_lines, c.public_api_changed,
                    c.deps_changed, c.gates_passed, c.reviews_passed)
    assert _rank(classify(bigger)) >= _rank(classify(c))

@given(changes, st.integers(0, 1000))
def test_more_lines_never_lowers_tier(c, extra):
    bigger = Change(c.paths, c.diff_lines + extra, c.public_api_changed,
                    c.deps_changed, c.gates_passed, c.reviews_passed)
    assert _rank(classify(bigger)) >= _rank(classify(c))

@given(changes)
def test_deterministic(c):
    assert decide(c) == decide(c)

@given(changes)
def test_failed_gates_never_merge(c):
    if not c.gates_passed:
        assert decide(c) == "reject"

@given(changes)
def test_high_risk_never_auto_merges(c):
    if classify(c) in ("A2", "A3"):
        assert decide(c) != "merge"
```

## Experiment E7: plant bugs, compare test styles

1. Have an agent write **example-based** unit tests for the engine (`tests/test_examples.py`).
2. Plant six realistic bugs, one at a time, for example:
   - a `min` where a `max` belongs in `classify`
   - `>` changed to `>=` on the 250-line threshold
   - the A3 glob list loses `**/migrations/**`
   - `deps_changed` ignored
   - `decide` checks tier before gates
   - an `or` turned into `and` for the A1 review rule
3. Run each suite against each bug. Record which suite catches which bug in `docs/pbt-catches.md`.
4. Keep a running list of **real** property-test failures during development: the property, the counterexample, the fix. Real catches matter more than planted ones.

Be honest in the write-up: property tests are evidence, not proof, and a weak property will pass while behaviour is still wrong.

## Checkpoint

- [ ] Engine and five properties pass locally
- [ ] Example-based suite written by an agent
- [ ] Six planted bugs run against both suites; table logged
