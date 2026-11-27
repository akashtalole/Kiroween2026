#!/usr/bin/env python3
"""Spec Gate linter for Kiro requirements.md files. Exit 0 = ready, 1 = findings, 2 = usage error."""
import re
import sys

VAGUE = ["fast", "quickly", "quick", "easy", "easily", "user-friendly", "intuitive", "robust", "scalable",
         "efficient", "seamless", "seamlessly", "appropriate", "appropriately", "as needed", "etc", "simple",
         "flexible", "reasonable", "soon", "many", "few", "some", "better", "optimal", "nice"]
EARS = re.compile(r"\b(WHEN|IF|WHILE|WHERE)\b.*\bSHALL\b|\bTHE\b.*\bSHALL\b", re.I)
REQ = re.compile(r"^#{2,3}\s+(R-[A-Z0-9]+-\d+)\b(.*)$")
CRIT = re.compile(r"^\s*(?:\d+\.|[-*])\s+(.*)$")
TAG = re.compile(r"\[(PBT|EX)\]")
NUMBER = re.compile(r"\d")


def lint(text: str) -> list[str]:
    findings: list[str] = []
    current, crit_count, in_criteria, in_questions = None, 0, False, False
    reqs: list[tuple[str, int]] = []

    def close():
        if current is not None:
            reqs.append((current, crit_count))

    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if re.search(r"\b(TBD|TODO)\b|\?\?\?", line):
            findings.append(f"line {n}: unresolved placeholder: {line.strip()}")
        m = REQ.match(line)
        if m:
            close()
            current, crit_count, in_criteria, in_questions = m.group(1), 0, False, False
            continue
        if re.match(r"^#{1,3}\s", line):
            if re.match(r"^#{2,3}\s+Open questions", line, re.I):
                close(); current = None; in_questions = True; in_criteria = False
            elif current is None:
                in_questions = False
            continue
        if line.lower().startswith("acceptance criteria"):
            in_criteria = True
            continue
        c = CRIT.match(line)
        if in_questions and c:
            if not re.search(r"default", c.group(1), re.I):
                findings.append(f"line {n}: open question has no recommended default: {c.group(1)[:70]}")
            continue
        if current and in_criteria and c:
            body = c.group(1)
            crit_count += 1
            if not TAG.search(body):
                findings.append(f"line {n}: {current} criterion not tagged [PBT] or [EX]")
            if not EARS.search(body):
                findings.append(f"line {n}: {current} criterion is not in EARS form (WHEN/IF/WHILE/WHERE ... SHALL)")
            for w in VAGUE:
                if re.search(rf"\b{re.escape(w)}\b", body, re.I) and not NUMBER.search(body):
                    findings.append(f"line {n}: {current} uses vague word '{w}' without a measurable number")
    close()
    if not reqs:
        findings.append("no requirements found (expected headings like '## R-POL-1 Title')")
    for rid, count in reqs:
        if count == 0:
            findings.append(f"{rid} has no acceptance criteria")
    ids = [r for r, _ in reqs]
    for rid in {r for r in ids if ids.count(r) > 1}:
        findings.append(f"duplicate requirement id {rid}")
    return findings


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: spec_lint.py <requirements.md>", file=sys.stderr)
        return 2
    try:
        text = open(argv[1], encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {argv[1]}: {e}", file=sys.stderr)
        return 2
    findings = lint(text)
    if not findings:
        print(f"Spec Gate: {argv[1]} is ready.")
        return 0
    print(f"Spec Gate: {len(findings)} finding(s) in {argv[1]}:")
    for f in findings:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
