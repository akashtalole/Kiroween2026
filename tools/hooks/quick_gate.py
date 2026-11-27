#!/usr/bin/env python3
"""Stop / PostFileSave hook: lint changed specs and run the fast test suites. Non-zero exit sends stderr to the agent."""
import subprocess
import sys

def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr)[-3000:]


def main(argv: list[str]) -> int:
    problems = []
    if "--tests-only" not in argv:
        changed = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split()
        changed += subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True).stdout.split()
        for f in sorted(set(changed)):
            if f.startswith(".kiro/specs/") and f.endswith("requirements.md") and "_templates" not in f:
                code, out = run([sys.executable, ".kiro/skills/spec-gate/scripts/spec_lint.py", f])
                if code:
                    problems.append(out)
    code, out = run([sys.executable, "-m", "pytest", "-q", "-x", "--no-header", "tests", "examples/policy-engine"])
    if code not in (0, 5):  # 5 = no tests collected
        problems.append("Tests failed:\n" + out)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    print("Quick gate: specs and fast tests are green.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
