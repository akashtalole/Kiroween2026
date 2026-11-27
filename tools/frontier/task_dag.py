#!/usr/bin/env python3
"""Dependency-aware scheduling of spec tasks for parallel agents.

tasks.md line syntax (extras are optional):
  - [ ] 3. Title (R-X-1.1) (after 1, 2) (files: src/a.py, src/b.py)
Tasks run in waves: a task waits for its `after` tasks, and two tasks in one wave never touch the same file,
so parallel worktrees merge without conflicts.
"""
from __future__ import annotations

import dataclasses
import re
import sys

LINE = re.compile(r"^\s*-\s*\[(?P<done>[ xX])\]\s*(?P<id>\d+)\.\s*(?P<title>.*)$")
AFTER = re.compile(r"\(after\s+([\d,\s]+)\)", re.I)
FILES = re.compile(r"\(files:\s*([^)]+)\)", re.I)


@dataclasses.dataclass(frozen=True)
class Task:
    id: int
    title: str
    done: bool
    after: frozenset
    files: frozenset


class CycleError(ValueError):
    pass


def parse(text: str) -> list[Task]:
    tasks = []
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        rest = m.group("title")
        after = frozenset(int(x) for x in re.findall(r"\d+", AFTER.search(rest).group(1))) if AFTER.search(rest) else frozenset()
        files = frozenset(f.strip() for f in FILES.search(rest).group(1).split(",") if f.strip()) if FILES.search(rest) else frozenset()
        title = FILES.sub("", AFTER.sub("", rest)).strip()
        tasks.append(Task(int(m.group("id")), title, m.group("done") != " ", after, files))
    return tasks


def waves(tasks: list[Task]) -> list[list[int]]:
    """Unfinished tasks grouped into waves; deps outside the list or already done count as satisfied."""
    todo = {t.id: t for t in tasks if not t.done}
    done = {t.id for t in tasks if t.done} | {d for t in tasks for d in t.after if d not in {x.id for x in tasks}}
    result = []
    while todo:
        ready = sorted(i for i, t in todo.items() if t.after <= done)
        if not ready:
            raise CycleError(f"dependency cycle among tasks {sorted(todo)}")
        wave, used = [], set()
        for i in ready:  # greedy: lowest id first, skip a task whose files clash with the wave
            if todo[i].files & used:
                continue
            wave.append(i)
            used |= todo[i].files
        result.append(wave)
        for i in wave:
            done.add(i)
            del todo[i]
    return result


def next_ready(tasks: list[Task]) -> list[int]:
    w = waves(tasks)
    return w[0] if w else []


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: task_dag.py <tasks.md>", file=sys.stderr)
        return 2
    tasks = parse(open(argv[1], encoding="utf-8").read())
    try:
        for n, w in enumerate(waves(tasks), 1):
            print(f"wave {n}: " + ", ".join(f"{i}. {next(t.title for t in tasks if t.id == i)}" for i in w))
    except CycleError as e:
        print(f"Cannot schedule: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
