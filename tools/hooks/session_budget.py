#!/usr/bin/env python3
"""SessionStart hook: print tonight's remaining credit budget into the agent's context (stdout is added on exit 0)."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from ledger import LEDGER, night_of  # noqa: E402
import datetime as dt  # noqa: E402


def budget() -> float:
    try:
        text = open("org/nightshift.yaml", encoding="utf-8").read()
        m = re.search(r"credits_per_night:\s*([\d.]+)", text)
        return float(m.group(1)) if m else 0.0
    except OSError:
        return 0.0


def spent(night: str) -> float:
    total = 0.0
    try:
        for line in open(LEDGER, encoding="utf-8"):
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("night") == night:
                total += float(e.get("credits", 0) or 0)
    except OSError:
        pass
    return total


def main() -> int:
    night = night_of(dt.datetime.now())
    b, s = budget(), spent(night)
    if b:
        print(f"Night Shift budget for night {night}: {b - s:.1f} of {b:.0f} credits left. "
              "If a task would exceed the per-task cap in org/nightshift.yaml, stop and report instead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
