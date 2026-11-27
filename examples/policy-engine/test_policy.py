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


# --- Rule properties added after mutation testing (tools/frontier/mutate.py) scored the suite 10/34:
# --- the original properties checked shape (monotonic, deterministic) but not the actual rules.
A3_SAMPLES = ["src/auth/login.py", "app/secrets/key.txt", "infra/main.tf", "db/migrations/001.sql"]
A0_SAMPLES = ["docs/guide.md", "docs/diagram.png", "README.md", "tests/test_x.py", "tests/fixtures/data.json",
              "src/pkg/test_y.py", "notes/plan.md"]


@given(changes, st.sampled_from(A3_SAMPLES))  # R-POL-1.3
def test_any_a3_path_makes_the_change_a3(c, a3):
    assert classify(Change(c.paths + (a3,), c.diff_lines, c.public_api_changed, c.deps_changed)) == "A3"


@given(st.lists(st.sampled_from(A0_SAMPLES), min_size=1, max_size=5), st.integers(0, 250))
def test_docs_and_tests_only_small_change_is_a0(ps, lines):
    c = Change(tuple(ps), lines)
    assert classify(c) == "A0" and decide(c) == "merge"


def test_empty_change_is_a0():
    assert classify(Change()) == "A0"


@given(st.sampled_from(A0_SAMPLES + ["src/app.py"]))
def test_large_diff_boundary_is_exactly_250(path):
    assert classify(Change((path,), 250)) in ("A0", "A1")
    assert classify(Change((path,), 251)) == "A2"


@given(changes)
def test_api_or_dependency_change_is_at_least_a2(c):
    if c.public_api_changed or c.deps_changed:
        assert _rank(classify(c)) >= 2


@given(st.integers(0, 250), st.integers(0, 2))
def test_a1_needs_two_reviews(lines, reviews):
    c = Change(("src/app.py",), lines, reviews_passed=reviews)
    assert classify(c) == "A1"
    assert decide(c) == ("merge" if reviews >= 2 else "queue_for_human")


def test_source_code_is_a1_not_a0():
    assert classify(Change(("src/app.py",), 10)) == "A1"


@given(st.booleans(), st.integers(0, 250))
def test_api_or_dependency_change_on_ordinary_code_is_exactly_a2(api, lines):
    c = Change(("src/app.py",), lines, public_api_changed=api, deps_changed=not api)
    assert classify(c) == "A2" and decide(c) == "queue_for_human"
