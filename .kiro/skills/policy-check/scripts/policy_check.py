#!/usr/bin/env python3
"""Run the Night Shift policy engine on the current git diff and print a JSON decision."""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "examples" / "policy-engine"))
from policy import Change, classify, decide  # noqa: E402

DEP_FILES = ("requirements.txt", "pyproject.toml", "package.json", "package-lock.json", "poetry.lock", "go.mod", "Cargo.toml")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--gates-passed", choices=["yes", "no"], required=True)
    ap.add_argument("--reviews", type=int, default=0)
    ap.add_argument("--public-api-changed", action="store_true")
    ap.add_argument("--deps-changed", action="store_true")
    ap.add_argument("--paths", nargs="*", help="override: changed paths (skips git)")
    ap.add_argument("--diff-lines", type=int, help="override: changed line count (skips git)")
    a = ap.parse_args()

    if a.paths is not None:
        paths, lines = a.paths, a.diff_lines or 0
    else:
        paths = [p for p in git("diff", "--name-only", a.base).splitlines() if p]
        lines = 0
        for row in git("diff", "--numstat", a.base).splitlines():
            add, rem, _ = row.split("\t", 2)
            lines += (int(add) if add.isdigit() else 0) + (int(rem) if rem.isdigit() else 0)
    deps = a.deps_changed or any(p.endswith(DEP_FILES) for p in paths)
    c = Change(tuple(paths), lines, a.public_api_changed, deps, a.gates_passed == "yes", a.reviews)
    signals = []
    if deps:
        signals.append("dependency change")
    if a.public_api_changed:
        signals.append("public API change")
    if lines > 250:
        signals.append(f"large diff ({lines} lines)")
    if classify(Change(tuple(paths))) == "A3":
        signals.append("touches an A3 path (auth, secrets, infra, migrations)")
    if not c.gates_passed:
        signals.append("a gate failed")
    print(json.dumps({"tier": classify(c), "decision": decide(c), "signals": signals,
                      "paths": len(paths), "diff_lines": lines, "reviews": a.reviews}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
