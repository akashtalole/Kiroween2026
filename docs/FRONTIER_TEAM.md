# Night Shift as a frontier engineering team

Kiro's *Frontier teams* page (https://kiro.dev/topics/frontier-teams/) describes five practices shared by the highest-performing teams it studied. This page shows how Night Shift turns each one into something you can clone, run and measure with Kiro's products. The page's results (median 4.5x, up to 20x on specific projects) belong to those teams; Night Shift reports only its own measured numbers.

## 1. Practices → mechanisms → Kiro products

| Frontier practice | Night Shift mechanism | Kiro product | Artifact |
|---|---|---|---|
| **Invest in agent context** | Always-on steering, a generated codebase map, per-role "must not" rules, bot memories | IDE + CLI (steering, auto inclusion), Crew (memory) | `.kiro/steering/*`, `tools/frontier/context_map.py`, Context Keeper bot |
| **Make intent explicit** | Spec Gate before any build; a question queue with recommended defaults | IDE spec mode, CLI headless analyst | `spec-gate` skill, `nightshift questions` |
| **Feed agents, don't babysit** | Ranked backlog; dependency-aware waves in parallel worktrees; overnight runs; cloud runs when the laptop sleeps | CLI headless, Crew bots and conductor mode, Web cloud sessions | `nightshift night`, `nightshift plan`, `nightshift cloud`, `crew/` |
| **Shift testing left** | Hooks gate every turn; property tests from requirements; **proof strength** (mutation score) as a CI floor | IDE spec PBT, hooks on IDE/CLI/Web | `.kiro/hooks/*`, `tools/frontier/mutate.py`, `docs/pbt-catches.md` |
| **Org-wide governance** | Least-privilege agents linted in CI; deterministic merge policy; independent multi-model review; budgets | Custom agents + permissions, Powers for distribution | `tools/frontier/agent_lint.py`, `policy-check`, `powers/night-shift` |

## 2. Who the humans are

Agents do the low-judgment work. People own the high-judgment work, which matches the frontier page's point that code review moves to interfaces and architecture.

| Role | Owns | Time per day |
|---|---|---|
| **Intent owner** | Writes intent paragraphs, answers the question queue, accepts or rejects defaults | 20–40 min |
| **Reviewer of record** | Decides tier A2/A3 items in the exception queue from evidence packs | 15–30 min |
| **Context steward** | Accepts steering changes proposed by the Context Keeper; owns `org/nightshift.yaml` | 10 min, weekly review |
| **Champion** | Rolls the model out to the next team, shares steering and the power | part-time |

## 3. Daily and weekly cadence

| When | What happens | Product |
|---|---|---|
| Hourly | Intake turns new issues into spec drafts; vague ones go to the question queue | Crew bot → CLI analyst |
| 21:30 | Intake check-in: what's ready for tonight | Crew |
| 22:00 | Night Conductor: `nightshift night` (waves, worktrees, multi-model review, policy, evidence) | Crew → CLI headless |
| Overnight | Web cloud sessions for tasks that should not need your machine (`nightshift cloud`) | Web |
| 07:00 | Boo's morning briefing: needs you, shipped, questions, numbers | Crew + touch-index skill |
| Every PR | Kiro review in CI; agent lint; context-map check; proof-strength floor | CLI headless in GitHub Actions |
| Monday | Proof-strength sweep; survivors become tasks | Context Keeper |
| Friday | Repeated reviewer findings become proposed steering rules | Context Keeper |

## 4. The autonomy ladder (how an org adopts it)

The frontier page warns that the first two weeks feel slower. The ladder makes that explicit: you climb a rung only when the metrics say so.

| Rung | What agents may do alone | Promote when |
|---|---|---|
| 0. Assist | Nothing merges without a human | Spec Gate pass rate above 80% for a week |
| 1. Docs and tests | Tier A0 auto-merges | Zero escapes from A0 for two weeks |
| 2. Internal code | Tier A1 auto-merges with two independent reviews | Proof strength ≥ 0.85 on touched modules; escapes ≤ 1 per 50 merges |
| 3. Overnight | Night Conductor runs unattended within budget | Zero-touch rate stable for two weeks; cost per merged task within budget |
| A2/A3 | **Always a human** | never automated |

This maps onto the page's four rollout phases: **Onboard** (one team, rung 0, this repo's labs), **Experiment** (first specs, experiments E1 to E8 in `docs/KIRO_FEATURE_PLAN.md`), **Scale** (share steering and the `night-shift` power; agent lint keeps new teams compliant), **Sustain** (a champion per team; the Context Keeper keeps context current).

## 5. Scoreboard (all measured from the ledger and CI, never estimated)

| Metric | Source | Why it matters |
|---|---|---|
| Zero-touch rate, touches per task, human seconds per merged task | `touch-index` skill on `ledger.ndjson` | The honest version of "minimal human intervention" |
| Proof strength | `tools/frontier/mutate.py` (CI floor 0.85 on the merge policy) | A green suite with weak tests is a false comfort |
| Escapes | `escape` ledger events | Whether autonomy is hurting quality |
| Lead time intent → merge | ledger timestamps | Whether the loop is actually faster |
| Credits per merged task | stream-json events | Whether it is affordable |
| Spec Gate pass rate, questions answered within a day | `nightshift questions`, ledger | Whether intent is the bottleneck |

## 6. Enterprise controls to evaluate (from the Kiro docs; verify on your plan)

The Kiro documentation lists enterprise topics including identity provider connection, governance, credit pooling, subscription management, managed updates, monitoring and tracking, API key governance, and data perimeters (VPC endpoints). Night Shift's own controls (agent lint, policy engine, budgets, ledger) are designed to sit *under* those, not replace them. Check what your organisation's plan includes before promising any of them.

## 7. Anti-patterns this setup is built to prevent

- **"The agent approved its own work."** Reviewers run in fresh sessions, on different models when configured, and a deterministic policy decides.
- **"Tests are green, so it's fine."** Proof strength measures whether the tests can fail.
- **"It kept making the same mistake."** The Context Keeper turns repeated findings into steering rules.
- **"We don't know how much a human did."** The touch logger and ledger count it.
- **"It quietly expanded its own permissions."** Agent lint runs in CI; deny rules always win.

## 8. Run it

```bash
python3 tools/frontier/agent_lint.py                     # governance
tools/nightshift/nightshift plan <capability>             # parallel-safe waves
tools/nightshift/nightshift questions                     # the question queue
tools/nightshift/nightshift night --review-models <model-a>,<model-b>
tools/nightshift/nightshift cloud <capability> --repo <owner/name>
python3 tools/frontier/mutate.py <module.py> <tests>      # proof strength
python3 tools/frontier/context_map.py                     # refresh agent context
```

Use model IDs your Kiro account offers for `--review-models`. Two different models give more independent reviews than two runs of one.
