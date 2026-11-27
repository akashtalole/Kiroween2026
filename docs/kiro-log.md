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

## 2026-11-27 E7 (early): mutation testing of the merge policy
Surface: none (local Python; drafted in a Claude Code session)
Metrics: proof strength 10/34 (0.29) with the original 5 properties → 32/35 (0.91) after 8 rule properties
Result: the original properties checked shape (monotonic, deterministic), not rules. Writing the missing ones exposed a real bug: root `README.md` was tier A1 instead of A0. CI now enforces a 0.85 floor.
Evidence: docs/pbt-catches.md, tools/frontier/mutate.py, .github/workflows/ci.yml
Surprise: the mutation tool's own first run scored 0/34 because the tests imported the original module; caught because 0 was implausible.

## 2026-11-27 Setup: frontier-team tooling drafted
Surface: none yet (Claude Code session; orchestrator tested with a fake kiro-cli)
What: agent governance linter (all 8 agents compliant), dependency-aware task waves, multi-model review panel, cloud runs, question queue, generated codebase map (auto-inclusion steering), `night-shift` power (plugin.json + 6 skills), Context Keeper bot, operating-model doc.
Next: import the power in Kiro (Powers → Add Custom Power → folder) and confirm keyword activation; try `--review-models` with two real model IDs.

## 2026-11-27 Setup: advanced frontier features built (round 5 "Yes" items)
Surface: none yet (Claude Code session; fake kiro-cli)
What: exhaustive merge-policy verification (1,152 inputs, all ordered pairs), cost-aware model routing with one escalation retry (`org/routing.json`), 5 injection canaries + `nightshift redteam`, failure drills in CI.
Result: 64 tests pass. Drills 4/4. Canaries: 5/5 held against a well-behaved fake agent, 0/5 against a fake agent that obeys everything (all four checks fire). The test exposed an inspector gap (untracked folders), now fixed.
Next: run `nightshift redteam` against the real Kiro builder agent and record the real canary score here.
