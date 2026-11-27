import json
import pathlib
import sys

import pytest
from hypothesis import given, strategies as st

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/frontier"))
import agent_lint  # noqa: E402
import mutate  # noqa: E402
import task_dag  # noqa: E402

# ---------------- task DAG ----------------
EXAMPLE = """- [x] 1. Model (R-A-1)
- [ ] 2. API (R-A-2) (after 1) (files: src/api.py)
- [ ] 3. CLI (R-A-3) (after 1) (files: src/cli.py)
- [ ] 4. Docs (after 2, 3) (files: README.md)
- [ ] 5. Fix API edge (after 1) (files: src/api.py)
"""


def test_example_waves_respect_deps_and_file_clashes():
    assert task_dag.waves(task_dag.parse(EXAMPLE)) == [[2, 3], [4, 5]]


def test_cycle_is_reported():
    with pytest.raises(task_dag.CycleError):
        task_dag.waves(task_dag.parse("- [ ] 1. a (after 2)\n- [ ] 2. b (after 1)\n"))


@st.composite
def dags(draw):
    n = draw(st.integers(1, 12))
    files = ["a", "b", "c", "d"]
    tasks = []
    for i in range(1, n + 1):
        after = draw(st.sets(st.integers(1, i - 1), max_size=3)) if i > 1 else set()
        tasks.append(task_dag.Task(i, f"t{i}", draw(st.booleans()) and draw(st.booleans()), frozenset(after),
                                   frozenset(draw(st.sets(st.sampled_from(files), max_size=2)))))
    return tasks


@given(dags())
def test_schedule_properties(tasks):
    w = task_dag.waves(tasks)
    flat = [i for wave in w for i in wave]
    todo = {t.id for t in tasks if not t.done}
    assert sorted(flat) == sorted(todo)                      # every unfinished task exactly once
    pos = {i: k for k, wave in enumerate(w) for i in wave}
    by_id = {t.id: t for t in tasks}
    for i in flat:
        for d in by_id[i].after:
            if d in pos:
                assert pos[d] < pos[i]                       # dependencies run in an earlier wave
    for wave in w:
        seen = set()
        for i in wave:
            assert not (by_id[i].files & seen)               # no two tasks in a wave touch the same file
            seen |= by_id[i].files
    assert task_dag.waves(tasks) == w                         # deterministic


# ---------------- governance ----------------
def test_repo_agents_are_compliant():
    assert agent_lint.main(["x", str(ROOT / ".kiro/agents")]) == 0


def test_linter_catches_a_writer_reviewer():
    bad = {"name": "reviewer", "description": "d", "tools": ["read", "write"],
           "permissions": {"rules": [{"capability": "fs_write", "match": ["src/**"], "effect": "allow"}]}}
    problems = agent_lint.lint_agent("reviewer", bad)
    assert any("read-only role has the write tool" in p for p in problems)


def test_linter_catches_wildcards_and_unscoped_shell():
    problems = agent_lint.lint_agent("builder", {"description": "d", "tools": ["*", "shell"]})
    assert any("wildcard" in p for p in problems) and any("shell allow" in p for p in problems)


# ---------------- mutation tool ----------------
def test_mutation_tool_kills_and_reports_survivors(tmp_path):
    (tmp_path / "m.py").write_text("def big(x):\n    return x > 10\n")
    (tmp_path / "test_m.py").write_text("from m import big\n\ndef test_big():\n    assert big(11) and not big(10)\n")
    r = mutate.run(tmp_path / "m.py", tmp_path / "test_m.py", None)
    assert r["mutants"] == 2 and r["killed"] == 2 and r["score"] == 1.0  # '>' -> '>=' and 10 -> 11 both caught


# ---------------- orchestrator additions ----------------
FAKE = str(ROOT / "tests/fakes/kiro-cli")


@pytest.fixture
def ns(monkeypatch, tmp_path):
    monkeypatch.setenv("NS_KIRO_BIN", FAKE)
    monkeypatch.setenv("NS_LEDGER", str(tmp_path / "ledger.ndjson"))
    monkeypatch.setenv("FAKE_KIRO_LOG", str(tmp_path / "calls.ndjson"))
    sys.path.insert(0, str(ROOT / "tools/nightshift"))
    import importlib
    import ns as mod
    return importlib.reload(mod)


def test_cloud_flags(ns):
    cmd = ns.build_cmd(None, cloud=True, repo="o/r")
    assert "--cloud" in cmd and cmd[cmd.index("--repo") + 1] == "o/r"


def test_review_panel_uses_one_session_per_model(ns, tmp_path):
    r = ns.review_panel("diff", ["model-a", "model-b"], sleep=lambda s: None)
    argvs = [json.loads(line)["argv"] for line in (tmp_path / "calls.ndjson").read_text().splitlines()]
    assert sorted(a[a.index("--model") + 1] for a in argvs) == ["model-a", "model-b"]
    assert all(a[a.index("--agent") + 1] == "reviewer" for a in argvs)
    assert r["verdict"] == "approve" and set(r["verdicts"]) == {"model-a", "model-b"}


def test_questions_lists_and_accepts_defaults(ns, tmp_path, monkeypatch):
    spec = tmp_path / ".kiro/specs/demo"
    spec.mkdir(parents=True)
    (spec / "requirements.md").write_text("## Open questions\n- Cache? Recommended default: no cache.\n")
    monkeypatch.setattr(ns, "ROOT", tmp_path)
    import argparse
    assert ns.cmd_questions(argparse.Namespace(accept_defaults=True)) == 0
    assert "Decision: default accepted" in (spec / "requirements.md").read_text()
    assert ns.cmd_questions(argparse.Namespace(accept_defaults=False)) == 0  # nothing left open


def test_power_skills_mirror_repo_skills():
    power = ROOT / "powers/night-shift"
    manifest = json.loads((power / "plugin.json").read_text())
    for field in ("$schema", "name", "version", "description", "author", "keywords"):
        assert manifest.get(field), field
    for sk in ["spec-gate", "policy-check", "evidence-pack", "touch-index", "morning-briefing"]:
        for f in (ROOT / ".kiro/skills" / sk).rglob("*"):
            if f.is_file():
                twin = power / "skills" / sk / f.relative_to(ROOT / ".kiro/skills" / sk)
                assert twin.read_bytes() == f.read_bytes(), f"{twin} is out of sync with {f}"
