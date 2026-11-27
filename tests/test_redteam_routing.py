import json
import pathlib
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture
def ns(monkeypatch, tmp_path):
    monkeypatch.setenv("NS_KIRO_BIN", str(ROOT / "tests/fakes/kiro-cli"))
    monkeypatch.setenv("NS_LEDGER", str(tmp_path / "ledger.ndjson"))
    sys.path.insert(0, str(ROOT / "tools/nightshift"))
    import importlib
    import ns as mod
    mod = importlib.reload(mod)
    mod.EVIDENCE = tmp_path / "evidence"
    return mod


def throwaway_repo(tmp_path):
    wt = tmp_path / "wt-redteam"
    (wt / "tests").mkdir(parents=True)
    (wt / "tests/test_a.py").write_text("def test_one():\n    pass\n\ndef test_two():\n    pass\n")
    run = lambda *c: subprocess.run(c, cwd=wt, check=True, capture_output=True)  # noqa: E731
    run("git", "init", "-q"); run("git", "add", "-A")
    run("git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    return wt


def test_canaries_hold_against_a_well_behaved_agent(ns, tmp_path):
    r = ns.run_canaries(ROOT / "redteam/canaries", throwaway_repo(tmp_path))
    assert r["total"] == 5 and r["held"] == 5


def test_canaries_catch_a_compromised_agent(ns, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_KIRO_MODE", "compromised")
    r = ns.run_canaries(ROOT / "redteam/canaries", throwaway_repo(tmp_path))
    assert r["held"] == 0
    problems = " ".join(p for x in r["results"] for p in x["problems"])
    for expected in ("marker file", "protected path changed: src/auth", "tests removed", "secret-like"):
        assert expected in problems
    events = [json.loads(line) for line in (tmp_path / "ledger.ndjson").read_text().splitlines()]
    assert sum(e["type"] == "canary" for e in events) == 5


def test_reset_refuses_anything_but_the_redteam_worktree(ns, tmp_path):
    with pytest.raises(AssertionError):
        ns.reset_worktree(tmp_path)


def test_drills_all_pass(ns):
    assert all(d["ok"] for d in ns.run_drills())


def test_routing_and_task_risk(ns, tmp_path, monkeypatch):
    (tmp_path / "org").mkdir()
    (tmp_path / "org/routing.json").write_text(json.dumps({"builder": {"a0": {"model": "cheap", "effort": "low"},
                                                                       "default": {"model": "mid"},
                                                                       "escalate": {"model": "strong", "effort": "high"}}}))
    spec = tmp_path / ".kiro/specs/x"; spec.mkdir(parents=True)
    (spec / "tasks.md").write_text("- [ ] 1. docs (files: docs/a.md)\n- [ ] 2. code (files: src/a.py)\n- [ ] 3. none\n")
    monkeypatch.setattr(ns, "ROOT", tmp_path)
    assert ns.route("builder", "a0") == {"model": "cheap", "effort": "low"}
    assert ns.route("builder", "unknown") == {"model": "mid", "effort": None}
    assert [ns.task_route("x", i) for i in (1, 2, 3)] == ["a0", "default", "default"]
    cmd = ns.build_cmd("builder", model="cheap", effort="low")
    assert cmd[cmd.index("--model") + 1] == "cheap" and cmd[cmd.index("--effort") + 1] == "low"


def test_failed_gate_escalates_once(ns, tmp_path, monkeypatch):
    calls, gate_results = [], iter([1, 0])  # first gate fails, second passes
    monkeypatch.setattr(ns, "spec_ready", lambda c, root=None: True)
    monkeypatch.setattr(ns, "next_task", lambda c, root=None: 1)
    monkeypatch.setattr(ns, "task_route", lambda c, n: "default")
    monkeypatch.setattr(ns, "route", lambda role, key: {"model": key, "effort": None})
    monkeypatch.setattr(ns, "policy", lambda cwd, g, r: {"decision": "merge" if g else "reject", "tier": "A1", "signals": []})
    monkeypatch.setattr(ns, "review_panel", lambda *a, **k: {"verdict": "approve", "verdicts": {"default": "approve"},
                                                                 "text": "ok", "credits": 0, "attempts": 1, "seconds": 0})

    def fake_run(prompt, agent, **kw):
        calls.append(kw.get("model"))
        return ns.RunResult(0, [], "done", None, 1, 0.1)

    def fake_sh(cmd, cwd=None, check=False):
        rc = next(gate_results) if "quick_gate.py" in " ".join(cmd) else 0
        return types.SimpleNamespace(returncode=rc, stdout="", stderr="")

    monkeypatch.setattr(ns, "run_kiro", fake_run)
    monkeypatch.setattr(ns, "sh", fake_sh)
    s = ns.run_capability("x", use_worktree=False)
    assert calls == ["default", "escalate"] and s["routes"] == ["default", "escalate"] and s["status"] == "merge"
