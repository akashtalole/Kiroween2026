import io
import json
import os

import scope_guard
import secret_scan
from hypothesis import given, strategies as st


def run_guard(monkeypatch, payload):
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.delenv("NS_ALLOW_A3", raising=False)
    return scope_guard.main()


def test_guard_blocks_auth(monkeypatch):
    assert run_guard(monkeypatch, {"tool_input": {"path": "src/auth/login.py"}}) == 2


def test_guard_blocks_env_but_not_example(monkeypatch):
    assert run_guard(monkeypatch, {"tool_input": {"file_path": ".env"}}) == 2
    assert run_guard(monkeypatch, {"tool_input": {"file_path": ".env.example"}}) == 0


def test_guard_allows_normal_code(monkeypatch):
    assert run_guard(monkeypatch, {"tool_input": {"path": "apps/chimera/src/grid.ts"}}) == 0


def test_guard_handles_absolute_paths(monkeypatch):
    assert run_guard(monkeypatch, {"x": {"filePath": os.getcwd() + "/infra/main.tf"}}) == 2


def test_guard_survives_garbage(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("not json"))
    assert scope_guard.main() == 0


@given(st.sampled_from(["auth", "secrets", "migrations"]), st.lists(st.sampled_from(["a", "b", "src"]), max_size=3))
def test_guard_blocks_protected_dirs_at_any_depth(protected, parents):
    path = "/".join(parents + [protected, "file.py"])
    assert scope_guard.blocked(path)


def test_secret_patterns_detected():
    fake_aws = "AKIA" + "ABCDEFGHIJKLMNOP"
    assert "AWS access key" in secret_scan.scan(f"key = '{fake_aws}'")
    assert secret_scan.scan("KIRO_API_KEY = os.environ['KIRO_API_KEY']") == []
    assert secret_scan.scan("nothing to see") == []
