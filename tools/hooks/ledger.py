#!/usr/bin/env python3
"""Append one event to ledger.ndjson. Usage: ledger.py <type> [key=value ...]. Never fails the calling hook."""
import datetime as dt
import json
import os
import sys

LEDGER = os.environ.get("NS_LEDGER", "ledger.ndjson")


def night_of(now: dt.datetime) -> str:
    # a "night" runs 12:00 to 12:00 so overnight work groups together
    return (now - dt.timedelta(hours=12)).date().isoformat()


def append(event: dict) -> None:
    now = dt.datetime.now()
    event.setdefault("ts", now.isoformat(timespec="seconds"))
    event.setdefault("night", night_of(now))
    if os.environ.get("NS_TASK"):
        event.setdefault("task", os.environ["NS_TASK"])
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        return 0
    ev = {"type": argv[1]}
    for kv in argv[2:]:
        if "=" in kv:
            k, v = kv.split("=", 1)
            ev[k] = v
    if argv[1] == "human_prompt":
        ev["chars"] = len(os.environ.get("USER_PROMPT", ""))
    try:
        append(ev)
    except OSError as e:
        print(f"ledger: could not write ({e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
