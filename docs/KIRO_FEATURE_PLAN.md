# Using every Kiro feature on purpose (Night Shift)

Companion to `docs/NIGHT_SHIFT.md`. The judges ask eight specific questions. The only way to answer them honestly is to **run small experiments and log the results as we build**. This plan assigns each feature a real job in Night Shift, a repo artifact judges can open, and one measurable experiment. The answers in `docs/WRITEUP.md` come from the log, not from memory.

Facts below were read from the Kiro docs on 2026-11-25. Where I could not confirm something, it says **verify**.

---

## 0. Surface constraints that shape the design

| Capability | IDE | CLI (V3) | Web | Crew |
|---|---|---|---|---|
| Specs (requirements, design, tasks) | yes | yes (execute) | yes (spec mode) | via projects / conductor |
| **Property-based tests from specs** | **yes** | **no** | **no** | not stated |
| Hooks | all triggers | file and task triggers (V3) | only Prompt Submit, Agent Stop, Session Start, Pre/Post Tool Use | not stated |
| Custom agents (`.kiro/agents/`) | yes | yes | yes (project-level) | not stated |
| Powers: install | yes | V3 | yes | not stated |
| Powers: create | yes | V3 | no | not stated |
| Headless / CI | no | **yes** (`--no-interactive`) | autonomous mode, schedule | scheduled jobs, bots |
| Merges code | no | no | **never merges automatically** | per bot limits |

Consequences:
1. **Specs and PBT work happens in the IDE** (that is the only place Kiro's own PBT runs). The code also carries ordinary Hypothesis/fast-check tests, which run anywhere.
2. **The CLI is the worker engine** (headless, hooks, custom agents).
3. **Web is the "second shift"**: autonomous mode and scheduled tasks open PRs. Kiro Web never merges, so merging is done by *our* policy engine in demo repos, which is consistent with the design.
4. **Crew is the always-on org layer**: bots, conductor mode, schedules, dashboards, memory.
5. Web needs a Pro-tier plan and a GitHub connection; **verify** the hackathon credits cover it before depending on it.

### Surface-per-job assignment

| Job | Surface | Why |
|---|---|---|
| Write and refine specs, steering, hooks, custom agents; run spec PBT | **IDE** | only surface with spec PBT; best for authoring |
| Headless task workers, gate runner, CI-style checks | **CLI** | `--no-interactive`, scriptable, worktrees |
| Nightly or recurring tasks that open PRs without my machine on | **Web** (schedule / autonomous mode) | runs in cloud sandbox |
| Persistent bots, conductor mode, briefing dashboard | **Crew** | designed for ongoing ownership |

---

## 1. The bake-off (answers "IDE, CLI, Web, Crew: how did they differ?")

**Experiment E1 (Day 1, about 90 min).** Give the *same* small task to all four surfaces, from a clean branch each:

> "Add a `--json` flag to the ledger export command, with requirements, tests, and docs."

Record in `docs/kiro-log.md` for each surface: wall-clock time, credits used, number of human messages, permission prompts, retries, whether tests passed first time, diff size, and one sentence on what felt different. Keep the diffs and transcripts (or links) as evidence.

Expected shape (hypotheses to *test*, not to assert): IDE best for interactive spec work; CLI best for repeatable automation; Web best for hands-off PRs; Crew best for long-running ownership. If the data disagrees, report the data.

---

## 2. Custom agents

**Job in the project:** each org role from `NIGHT_SHIFT.md` section 4 is a project-level agent in `.kiro/agents/` (Markdown format, since system prompts are long): `analyst`, `architect`, `builder`, `tester`, `reviewer`, `security`, `scribe`, `release`. Fields used: `tools` (least privilege), `excludedTools`, `resources` (steering and spec files loaded as context), `includeMcpJson`, `includePowers`.

**Where tried:** CLI headless (primary), IDE (switching in UI), Web (project-level agents load there too).

**Artifact:** `.kiro/agents/*.md`, plus `docs/agent-ablation.md`.

**Experiment E2 (Day 2):** run 5 identical tasks twice: once with the default agent, once with the `builder` agent. Compare permission prompts, off-scope file edits, retries to green, and credits. Also compare a single `reviewer` fresh-context review vs the builder self-reviewing, counting defects caught.

**Measure:** prompts per task, out-of-scope edits (via a scope-guard hook count), retries, defects found by review.

---

## 3. Hooks

Hooks live in `.kiro/hooks/*.json`. Schema (from the docs): `{"version":"v1","hooks":[{"name","trigger","matcher","action":{"type":"command"|"agent",...}}]}`. Command hooks receive session context as JSON on stdin. Confirmed example trigger name in the docs: `PostFileSave`. **Verify exact identifiers** for the others on the Hook types page before writing each file.

| Hook | Trigger (docs name) | Surface | Automates | Benefit to measure |
|---|---|---|---|---|
| `test-on-save` | File Save | IDE, CLI V3 | run tests for the saved file | feedback latency; failures caught before commit |
| `spec-gate` | Pre Task Execution | IDE, CLI V3 | lint requirements for vagueness/missing criteria; park task with a question | tasks started on bad specs (target: 0) |
| `scope-guard` | Pre Tool Use (write tools) | IDE, CLI, **Web** | block writes outside the role's allowed paths | off-scope edits prevented (count) |
| `secret-scan` | Pre Tool Use or File Save | all | stop commits containing secrets | incidents blocked |
| `gate-on-stop` | Agent Stop | IDE, CLI, **Web** | run the Correctness Gate; feed failures back to the agent | retries done without a human |
| `ledger-on-task` | Post Task Execution | IDE, CLI V3 | append credits, retries, evidence links to `ledger.ndjson` | log completeness |
| `touch-logger` | Prompt Submit | IDE, CLI, **Web** | record every human prompt as a "touch" in the ledger | makes Human Touch Index automatic and honest |
| `session-budget` | Session Start | IDE, CLI V3, **Web** | inject remaining credit budget and today's rules into context | overspend avoided |

Note: the docs say CLI Prompt Submit hooks cannot block; `touch-logger` only logs, so that is fine. Whether Pre Task Execution can block is something to **verify**; if it cannot, `spec-gate` runs as an Agent Stop check plus a CI check.

**Artifact:** `.kiro/hooks/*.json`, `docs/hook-impact.md` (counts per hook from the ledger).

**Experiment E3 (Day 3):** run the same 5 tasks with hooks off, then on; compare retries, off-scope edits, and human prompts.

---

## 4. Spec-driven development vs vibe coding

**Spec structure (one spec per capability):**
- `requirements.md`: IDs `R-<area>-<n>`, EARS acceptance criteria, each tagged `[PBT]` (universal property) or `[EX]` (example-based, e.g. UI or external service).
- `design.md`: includes a **Correctness properties** section mapping each property to requirement IDs.
- `tasks.md`: each task references requirement IDs and names the test that proves it; PBT tasks are not optional for `[PBT]` criteria.
- Brownfield (Lazarus): specs are generated *from the existing codebase first*, then edited.

**Artifact:** `.kiro/specs/<capability>/{requirements,design,tasks}.md`, `.kiro/specs/_templates/`.

**Experiment E4 (Day 2, about 2 hours):** implement one real feature twice on separate branches: the policy engine's "dependency change raises tier" rule. Branch A: vibe coding (chat prompts only). Branch B: spec first. Record: prompts used, rework cycles, bugs found later by PBT, time, and how closely behaviour matches intent. Publish both transcripts or summaries.

---

## 5. Steering

**Layers** (`.kiro/steering/`): `product.md`, `tech.md`, `structure.md`, plus org rules (`security.md`, `testing.md`, `release.md`, `style.md`) and role "must not" files. **Verify** whether steering inclusion modes (always, file-matched, manual) are available in your version, and use them to keep context small.

**Experiment E5 (Day 2): steering ablation.** Same 5 tasks under three conditions:
- (a) no steering,
- (b) terse rules ("use X, never Y"),
- (c) rich steering: rule + *why* + a good example + an anti-pattern + a definition-of-done checklist.

Score each output against a fixed rubric (convention violations, missing tests, wrong libraries, security rule breaches). My hypothesis is that (c) wins, specifically because of examples and anti-patterns, but the write-up reports the measured winner.

**Artifact:** `.kiro/steering/*`, `docs/steering-ablation.md` with the rubric and scores.

---

## 6. MCP

Two custom MCP servers, because they enable things that would otherwise be hard:

1. **`nightshift-mcp`** (Python): tools `queue.list`, `queue.next`, `ledger.append`, `ledger.stats`, `policy.classify(diff)`, `evidence.get(task)`. Any surface (IDE chat, CLI worker, Crew bot) reads the same org state. *Otherwise impossible:* agents on different surfaces would not share a queue or ledger.
2. **`legacy-oracle-mcp`** (for Lazarus): starts the legacy Perl app in a sandbox and exposes `request(method, path, body)` returning the real response. *Otherwise difficult:* the agent can interrogate actual legacy behaviour while writing specs and tests instead of guessing from reading Perl.

Plus the GitHub MCP for issues and PRs. Confirmed from the docs: custom agents can pin MCP tools via `tools` selectors and `includeMcpJson`.

**Experiment E6 (Day 4):** write Lazarus characterization specs with and without `legacy-oracle-mcp`; compare behaviours found, spec errors later contradicted by the oracle, and time.

**Artifact:** `packages/nightshift-mcp/`, `apps/lazarus/oracle-mcp/`, `.kiro/settings/mcp.json`, `docs/mcp-impact.md`.

---

## 7. Property-based testing

Kiro's spec PBT runs **in the IDE only**; it extracts properties from EARS requirements and generates many cases. We use it there, and also write Hypothesis (Python) and fast-check (TypeScript) tests that run in CI and headless.

| Requirement type enabled for PBT | Property |
|---|---|
| Policy engine | Tier is monotonic: adding a changed file, a dependency diff, or lines never lowers the tier |
| Policy engine | Same inputs always give the same decision (determinism) |
| Ledger | Append then parse round-trips; the stats are invariant to event order |
| Spec Gate lint | Idempotent; never passes a spec with an empty acceptance-criteria list |
| Chimera recalculation | Result independent of evaluation order; cycles always detected |
| Lazarus parity | Old and new agree on all generated valid requests, or the difference is in the approved-differences list |
| Evidence pack | Always contains every required section for any gate result combination |

**Experiment E7 (Day 3): seeded bugs.** Plant 6 realistic bugs across the policy engine and Chimera recalculation. Run (a) the example-based unit tests the agent wrote and (b) the PBT. Count which bugs each finds. Also keep a running `docs/pbt-catches.md`: every real PBT failure during development, with the property, the counterexample, and the fix. Real catches matter more than planted ones.

---

## 8. Powers

Powers are directories with `plugin.json` (manifest and activation keywords), `skills/` (Agent Skills), and optional `mcp.json`. They load on demand by keyword instead of loading every tool up front.

1. **Create our own: `night-shift` power.** Contains the Spec Gate skill, the steering summary, and the `nightshift-mcp` config. Install it on IDE and CLI and Web (install is supported on all three; creating is IDE and CLI V3). Demonstrates keyword activation vs always-on MCP.
2. **Trial third-party powers from the registry**, using the current registry list (158 powers on 2026-11-25; **verify** availability in your account). Candidates by relevance, not endorsement: a code-quality/review power (e.g. Qodo), a docs power (e.g. Mintlify), a security power (e.g. Pi Security, Native Security), a UI test power (e.g. BrowserStack, Katalon), and an enterprise intake power (e.g. Atlassian for Jira/Confluence). Trial each for 20 minutes on Day 2 against a concrete task; **keep only those that measurably help, drop the rest, and say so**.

**Experiment E8 (Day 2):** measure context size (tool definitions loaded) and task quality with the `night-shift` capabilities as (a) plain always-on MCP vs (b) a power.

**Artifact:** `powers/night-shift/`, `docs/powers-trial.md` (what we tried, what we kept, why).

---

## 9. Crew and Web specifics

- **Crew:** bots (`intake`, `pipeline-health`, `docs-sync`, `cost-governor`, `morning-briefing`), conductor mode for the nightly goal with worker sessions, scheduled jobs, memory (teach it "new endpoints need a property test" and verify later tasks follow it), dashboard. Separate `night-shift-crew` repo for the bonus prize.
- **Web:** use Spec mode and autonomous mode for one Chimera task and a scheduled recurring task (for example weekly dependency PRs); use cloud configuration to bring our `.kiro` agents, hooks, powers and MCP into cloud sessions. Review and merge via the policy engine.

---

## 10. Evidence discipline

- Every experiment writes one entry to `docs/kiro-log.md` (template below) the same day.
- A hook (`ledger-on-task`) appends credits and counts automatically; human observations are added by hand.
- `docs/WRITEUP.md` may only state results that have a log entry. If an experiment fails or shows no difference, we say so.

```
## <date> E<n>: <title>
Surface: IDE|CLI|Web|Crew     Agent: <name>     Model/effort: <...>
Setup: <conditions A/B>
Metrics: time=<..> credits=<..> human_msgs=<..> prompts=<..> retries=<..> defects=<..>
Result: <what happened, one paragraph>
Evidence: <paths / links>
Surprise: <what I did not expect>
```

---

## 11. Schedule for the experiments (fits the 9-day plan)

| Day | Experiments |
|---|---|
| Nov 25-26 | Install CLI, Crew; headless smoke test; **E1 bake-off** |
| Nov 27 | **E2 agents**, **E5 steering ablation**, **E8 powers**; third-party power trials; **E4 vibe vs spec** |
| Nov 28 | **E3 hooks** on/off; **E7 seeded bugs** and PBT in IDE |
| Nov 29-30 | **E6 oracle MCP** during Lazarus; Crew bots and memory test; Web scheduled task |
| Dec 1 | Fill gaps; compute final numbers from the ledger |
| Dec 2 | Complete `WRITEUP.md` from the log; record video |

Credit note: each experiment is small (a handful of tasks). Budget about 10 to 15 percent of total credits for experiments; track actuals in the log.

---

## 12. Definition of done for "used every feature"

- [ ] Four surfaces used, E1 results logged
- [ ] 8 custom agents committed, E2 results logged
- [ ] 8 hooks committed and firing, E3 results logged
- [ ] 4 or more specs with EARS and `[PBT]` tags, E4 comparison logged
- [ ] Steering layers committed, E5 ablation logged
- [ ] 2 custom MCP servers plus GitHub MCP, E6 logged
- [ ] PBT: IDE spec PBT run on at least 3 specs, Hypothesis/fast-check in CI, E7 and `pbt-catches.md`
- [ ] 1 custom power plus trial notes on third-party powers, E8 logged
