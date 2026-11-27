import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FAKE = str(ROOT / "tests/fakes/kiro-cli")


@pytest.fixture
def ns(monkeypatch, tmp_path):
    monkeypatch.setenv("NS_KIRO_BIN", FAKE)
    monkeypatch.setenv("NS_LEDGER", str(tmp_path / "ledger.ndjson"))
    monkeypatch.setenv("FAKE_KIRO_LOG", str(tmp_path / "calls.ndjson"))
    sys.path.insert(0, str(ROOT / "tools/nightshift"))
    import importlib
    import ns as mod
    mod = importlib.reload(mod)
    mod.EVIDENCE = tmp_path / "evidence"
    return mod


def calls(tmp_path):
    p = tmp_path / "calls.ndjson"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def test_build_cmd_is_headless_scoped_and_structured(ns):
    cmd = ns.build_cmd("reviewer", sandbox=True, require_mcp=True)
    assert cmd[:4] == [ns.KIRO, "chat", "--v3", "--no-interactive"]
    assert "--output-format" in cmd and "stream-json" in cmd
    assert "--trust-tools=read,grep,glob" in cmd and "--sandbox" in cmd and "--require-mcp-startup" in cmd
    assert not any("trust-all" in c for c in cmd)


def test_every_role_has_least_privilege_trust(ns):
    assert "write" not in ns.ROLE_TRUST["reviewer"] and "shell" not in ns.ROLE_TRUST["reviewer"]
    assert all(r in ns.ROLE_TRUST for r in ["analyst", "architect", "builder", "tester", "reviewer", "security", "scribe", "release"])


def test_run_ok_parses_text_and_credits(ns, tmp_path):
    r = ns.run_kiro("hello", "reviewer", sleep=lambda s: None)
    assert r.ok and "Verdict: approve" in r.text and r.credits == 1.5 and r.attempts == 1
    assert calls(tmp_path)[0]["prompt"] == "hello"  # prompt went via stdin


def test_throttling_is_retried_with_backoff(ns, tmp_path, monkeypatch):
    monkeypatch.setenv("FAKE_KIRO_MODE", "throttle_once")
    monkeypatch.setenv("FAKE_KIRO_STATE", str(tmp_path / "state"))
    waits = []
    r = ns.run_kiro("x", "builder", sleep=waits.append)
    assert r.ok and r.attempts == 2 and waits == [2]


def test_non_retryable_failure_is_returned_not_retried(ns, monkeypatch):
    monkeypatch.setenv("FAKE_KIRO_MODE", "fail")
    r = ns.run_kiro("x", "builder", sleep=lambda s: pytest.fail("should not sleep"))
    assert not r.ok and r.attempts == 1 and r.error["message"] == "boom"


@pytest.mark.parametrize("mode", ["agent_missing", "mcp_fail"])
def test_config_errors_stop_immediately(ns, monkeypatch, mode):
    monkeypatch.setenv("FAKE_KIRO_MODE", mode)
    with pytest.raises(ns.ConfigError):
        ns.run_kiro("x", "builder", sleep=lambda s: None)


def test_verdict_parsing(ns):
    assert ns.verdict_of("Verdict: approve\n...") == "approve"
    assert ns.verdict_of("**Verdict:** Request-changes") == "request-changes"
    assert ns.verdict_of("no idea") == "unknown"


def test_unready_spec_is_parked_and_never_calls_kiro(ns, tmp_path):
    s = ns.run_capability("does-not-exist", use_worktree=False)
    assert s["status"] == "parked" and calls(tmp_path) == []
    assert json.loads((tmp_path / "ledger.ndjson").read_text().splitlines()[-1])["type"] == "parked"


def test_doctor_with_fake_cli(ns, capsys):
    import argparse
    assert ns.cmd_doctor(argparse.Namespace()) == 0
    out = capsys.readouterr().out
    assert "kiro-cli 3.9.9" in out and "MISSING" not in out


def test_workflow_command_reports_outcome(ns, tmp_path):
    assert ns.main(["workflow", "night-feature", "task=demo", "--timeout", "600"]) == 0
    assert "--agent" not in calls(tmp_path)[0]["argv"]
    ev = json.loads((tmp_path / "ledger.ndjson").read_text().splitlines()[-1])
    assert ev["type"] == "workflow" and ev["outcome"] == "completed"
