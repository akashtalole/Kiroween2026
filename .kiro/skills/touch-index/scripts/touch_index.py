#!/usr/bin/env python3
"""Compute the Human Touch Index from an append-only ledger (NDJSON)."""
import argparse
import json
import sys
from collections import defaultdict

TOUCH_TYPES = {"human_prompt", "human_approval", "human_edit"}


def load(path: str, night: str | None = None) -> list[dict]:
    events = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                print(f"skipping malformed line {n}", file=sys.stderr)
                continue
            if night is None or e.get("night") == night:
                events.append(e)
    return events


def compute(events: list[dict]) -> dict:
    tasks = {e["task"]: e for e in events if e.get("type") == "task_done" and "task" in e}
    touches = defaultdict(int)
    seconds = defaultdict(float)
    for e in events:
        if e.get("type") in TOUCH_TYPES:
            touches[e.get("task", "_none")] += 1
            seconds[e.get("task", "_none")] += float(e.get("seconds", 0) or 0)
    merged = [t for t, e in tasks.items() if e.get("merged")]
    zero_touch = [t for t in merged if touches[t] == 0]
    n_tasks = len(tasks)
    return {
        "tasks_done": n_tasks,
        "merged": len(merged),
        "zero_touch_merged": len(zero_touch),
        "zero_touch_rate": round(len(zero_touch) / len(merged), 3) if merged else None,
        "touches_per_task": round(sum(touches[t] for t in tasks) / n_tasks, 3) if n_tasks else None,
        "human_seconds_per_merged_task": round(sum(seconds[t] for t in merged) / len(merged), 1) if merged else None,
        "retries_per_task": round(sum(int(e.get("retries", 0)) for e in tasks.values()) / n_tasks, 3) if n_tasks else None,
        "credits_per_merged_task": round(sum(float(tasks[t].get("credits", 0)) for t in merged) / len(merged), 2) if merged else None,
        "escapes": sum(1 for e in events if e.get("type") == "escape"),
        "untracked_touches": touches["_none"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--night")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        m = compute(load(a.ledger, a.night))
    except OSError as e:
        print(f"cannot read ledger: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(m, indent=2))
    else:
        for k, v in m.items():
            print(f"{k.replace('_', ' '):32} {'n/a' if v is None else v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
