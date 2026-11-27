#!/usr/bin/env python3
"""Secret scanner. Modes: --hook (PreToolUse payload on stdin), --diff (git working tree + staged), FILES... ."""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _payload import TEXT_KEYS, read_stdin, walk  # noqa: E402

PATTERNS = {
    "AWS access key": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "GitHub token": r"\b(ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b",
    "Slack token": r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b",
    "OpenAI-style key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "Kiro API key assignment": r"KIRO_API_KEY\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{12,}",
}


def scan(text: str) -> list[str]:
    return [name for name, pat in PATTERNS.items() if re.search(pat, text)]


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "--hook":
        text = "\n".join(walk(read_stdin(), TEXT_KEYS))
        source = "the content being written"
    elif len(argv) > 1 and argv[1] == "--diff":
        text = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True).stdout
        source = "the uncommitted diff"
    else:
        text = "".join(open(f, encoding="utf-8", errors="ignore").read() for f in argv[1:])
        source = ", ".join(argv[1:]) or "nothing"
    found = scan(text)
    if found:
        print(f"Secret scan: possible {', '.join(found)} in {source}. Use an environment variable instead "
              "(see .kiro/steering/security.md).", file=sys.stderr)
        return 2
    if len(argv) > 1 and argv[1] == "--diff":
        print("Secret scan: no secret patterns in the uncommitted diff.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
