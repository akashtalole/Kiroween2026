# How we used Kiro (write-up template)

> **Rule:** every claim here must link to an entry in `docs/kiro-log.md` or a file in the repo. Replace each `[FILL]` with measured results. Delete any sentence you cannot back with evidence. Negative and null results are welcome and increase credibility.

Project: **Night Shift**, a Skeleton Crew submission with two apps (Lazarus, Chimera) and a separate Kiro Crew app repo. See `docs/NIGHT_SHIFT.md` and `docs/KIRO_FEATURE_PLAN.md`.

---

## Kiro IDE, CLI, Web, Crew: how did they differ?

What we used each for:
- **IDE:** [FILL: specs, steering, hooks and agent authoring, spec PBT]
- **CLI:** [FILL: headless workers, gates, worktrees]
- **Web:** [FILL: spec mode, autonomous mode, scheduled PRs, cloud configuration]
- **Crew:** [FILL: bots, conductor mode, schedules, dashboard, memory]

Same-task bake-off (E1): [FILL: table of time, credits, human messages, retries, result per surface]

Verdict: [FILL: where each surface was clearly best, and where our expectation was wrong]

## Custom agents

Agents created: [FILL: list from `.kiro/agents/`]. Tried in: [FILL: CLI, IDE, Web].
Impact (E2): [FILL: permission prompts, off-scope edits, retries, review defects: default vs role agent]
Most useful design decision: [FILL]. What did not help: [FILL]

## Agent hooks

Hooks and what they automated: [FILL: table from `docs/hook-impact.md`]
Effect on the build (E3, hooks off vs on): [FILL: retries, off-scope edits, human prompts]
Hook we would not repeat: [FILL]

## Spec-driven development

Structure: [FILL: one spec per capability; EARS IDs; `[PBT]` vs `[EX]` tags; properties in design; tasks reference requirements]
Brownfield use (Lazarus): [FILL: specs generated from existing code, then corrected]
Spec vs vibe coding (E4): [FILL: prompts, rework, later bugs, time for each branch]
Where specs were slower or unnecessary: [FILL]

## Steering docs

Layers: [FILL]
Ablation (E5): [FILL: none vs terse vs rich; rubric scores]
Strategy with the biggest effect: [FILL: measured]

## MCP

Servers: `nightshift-mcp`, `legacy-oracle-mcp`, GitHub MCP. [FILL: tools used]
What it enabled (E6): [FILL: shared queue and ledger across surfaces; live legacy behaviour; what was found with vs without]
Limits and problems: [FILL]

## Property-based testing

Requirements enabled for PBT: [FILL: list from the table in the plan]
Real catches (from `docs/pbt-catches.md`): [FILL: property, counterexample, fix]
Seeded-bug comparison (E7): [FILL: bugs found by unit tests vs PBT]
Where PBT was not appropriate: [FILL]

## Kiro powers

Created: `night-shift` power. [FILL: contents, surfaces installed on, activation behaviour, context size vs always-on MCP (E8)]
Third-party powers trialled: [FILL: each with what it did, kept or dropped, why]
Integrations we would not otherwise have used: [FILL]

---

## Appendix: numbers

Human Touch Index across nights: [FILL: from `ledger.ndjson`: zero-touch rate, touches per task, human seconds per merged task, retries, credits per merged task, escapes]
First night vs last night: [FILL]
What a human still had to do: [FILL]
