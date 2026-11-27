---
name: spec-gate
description: Check a Kiro requirements.md for vague words, missing or untestable acceptance criteria, missing EARS form, missing [PBT]/[EX] tags and unanswered questions. Use before any design or build work starts, or when someone asks whether a spec is ready.
---
# Spec Gate

Nothing is built from a vague wish. Run the linter on the requirements file:

```bash
python3 .kiro/skills/spec-gate/scripts/spec_lint.py .kiro/specs/<capability>/requirements.md
```

- Exit code `0`: the spec is ready. Say so in one line.
- Exit code `1`: print each finding, then fix it (if you are the analyst) or send it back with the finding list (if you are anyone else).

What it checks:
1. Every requirement has an ID like `R-POL-1` and at least one acceptance criterion.
2. Every criterion uses EARS wording (`WHEN`, `IF … THEN`, `WHILE`, `WHERE` or `THE … SHALL`).
3. Every criterion is tagged `[PBT]` or `[EX]`.
4. No vague words without a number (fast, quickly, easy, user-friendly, robust, scalable, efficient, seamless, appropriate, etc.).
5. No `TBD` / `TODO` / `???`, and every open question has a recommended default.

When you tell a human about a failure, keep the house style: one light line, then the exact fix. Example:
> This spec is too vague to haunt anyone. R-API-2 says "fast": try "WHEN 100 users load the page, THE system SHALL respond in under 300 ms".
