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
    bigger = Change(c.paths + (extra,), c.diff_lines, c.public_api_changed, c.deps_changed,
                    c.gates_passed, c.reviews_passed)
    assert _rank(classify(bigger)) >= _rank(classify(c))

@given(changes, st.integers(0, 1000))
def test_more_lines_never_lowers_tier(c, extra):
    bigger = Change(c.paths, c.diff_lines + extra, c.public_api_changed, c.deps_changed,
                    c.gates_passed, c.reviews_passed)
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
