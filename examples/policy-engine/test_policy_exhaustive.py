"""Exhaustive check of the merge policy over its whole bounded input space.

Paths only matter through their class (none, A0, ordinary code, A3), and line counts only matter around the
250-line threshold, so every behaviourally distinct input is enumerated below: 8 path-class sets x 6 line counts
x 2 x 2 (API, deps) x 2 (gates) x 3 (reviews) = 1,152 changes. Every rule is checked on every one, and
monotonicity is checked on every ordered pair where one change adds signals to the other.
"""
import itertools

from policy import Change, _rank, classify, decide

CLASS_PATH = {"A0": "docs/guide.md", "code": "src/app.py", "A3": "src/auth/login.py"}
CLASS_SETS = [frozenset(c) for n in range(4) for c in itertools.combinations(CLASS_PATH, n)]
LINES = [0, 1, 249, 250, 251, 1000]
ALL = [(cs, ln, api, deps, g, rv) for cs in CLASS_SETS for ln in LINES for api in (False, True)
       for deps in (False, True) for g in (False, True) for rv in (0, 1, 2)]


def mk(cs, ln, api, deps, g, rv):
    return Change(tuple(CLASS_PATH[c] for c in sorted(cs)), ln, api, deps, g, rv)


def expected_tier(cs, ln, api, deps):
    if "A3" in cs:
        return "A3"
    if ln > 250 or api or deps:
        return "A2"
    return "A1" if "code" in cs else "A0"


def expected_decision(tier, gates, reviews):
    if not gates:
        return "reject"
    if tier in ("A2", "A3") or (tier == "A1" and reviews < 2):
        return "queue_for_human"
    return "merge"


def test_space_size():
    assert len(ALL) == 8 * 6 * 2 * 2 * 2 * 3 == 1152


def test_every_input_matches_the_written_rules():
    for args in ALL:
        cs, ln, api, deps, g, rv = args
        c = mk(*args)
        tier = expected_tier(cs, ln, api, deps)
        assert classify(c) == tier, args
        assert decide(c) == expected_decision(tier, g, rv), args


def test_monotonic_on_every_ordered_pair():
    sig = [(cs, ln, api, deps) for cs in CLASS_SETS for ln in LINES for api in (False, True) for deps in (False, True)]
    tiers = {s: _rank(classify(mk(*s, True, 2))) for s in sig}
    for a, b in itertools.product(sig, repeat=2):
        if a[0] <= b[0] and a[1] <= b[1] and a[2] <= b[2] and a[3] <= b[3]:
            assert tiers[a] <= tiers[b], (a, b)
