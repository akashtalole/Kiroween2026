# Kiro evidence log

One entry per experiment or notable event, written the same day. `docs/WRITEUP.md` may only cite what is here.

## 2026-11-27 Setup: initial .kiro configuration drafted
Surface: none yet (drafted outside Kiro, in a Claude Code session)
What: first versions of steering (6 files), role agents (8), skills (5, with tested scripts), hooks (7; 2 disabled until trigger names are verified), spec templates, Crew bot charters (6).
Next: load each in Kiro IDE and CLI, fix anything Kiro rejects, and record what changed here. Specs themselves are to be created in Kiro.
Evidence: commit history; `python3 -m pytest -q tests examples/policy-engine` (25 passed).

<!-- template
## <date> E<n>: <title>
Surface: IDE|CLI|Web|Crew     Agent: <name>
Setup: <conditions A/B>
Metrics: time=<..> credits=<..> human_msgs=<..> prompts=<..> retries=<..> defects=<..>
Result: <one paragraph>
Evidence: <paths / links>
Surprise: <what you did not expect>
-->

## 2026-11-27 Setup: Kiro CLI automation drafted
Surface: none yet (drafted outside Kiro, in a Claude Code session; tested against a fake kiro-cli only)
What: `tools/nightshift` orchestrator (headless stream-json runs, throttling backoff, exit-code handling, worktrees, independent review, policy decision, evidence, ledger), 3 workflow recipes, CI review and nightly jobs.
Test: 36 tests pass; an end-to-end `night` run with the fake CLI parked a vague spec and took a ready one to `merge` (A1) with evidence and ledger events.
Next: run `nightshift doctor` and one real `nightshift run --in-place` with the real Kiro CLI; record the real stream-json event fields and credits here.
