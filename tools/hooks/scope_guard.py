#!/usr/bin/env python3
"""PreToolUse hook: block agent writes to human-only paths. Non-zero exit blocks the tool; stderr goes to the agent."""
import os
import sys
from fnmatch import fnmatch

sys.path.insert(0, os.path.dirname(__file__))
from _payload import PATH_KEYS, read_stdin, walk  # noqa: E402

PROTECTED = ["**/auth/**", "auth/**", "**/secrets/**", "secrets/**", "infra/**", "**/migrations/**", "migrations/**",
             ".env", "**/.env", ".env.*", "**/.env.*", ".git/**", "org/nightshift.yaml"]


def blocked(path: str) -> bool:
    p = path.replace("\\", "/")
    root = os.getcwd().replace("\\", "/").rstrip("/") + "/"
    if p.startswith(root):
        p = p[len(root):]
    p = p.lstrip("./") if p.startswith("./") else p
    if p.endswith(".env.example"):
        return False
    return any(fnmatch(p, g) for g in PROTECTED)


def main() -> int:
    if os.environ.get("NS_ALLOW_A3") == "1":
        return 0
    hits = sorted({p for p in walk(read_stdin(), PATH_KEYS) if blocked(p)})
    if hits:
        print("Scope guard: these paths are human-only in Night Shift (tier A3 or secrets): " + ", ".join(hits)
              + ". Stop and add a note to the evidence pack asking a human; do not work around this.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
