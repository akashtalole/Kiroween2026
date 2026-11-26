# Devpost submission draft

Paste-ready text for the Devpost form. Replace every `[MEASURED: ...]` with a real number from `ledger.ndjson` / `docs/kiro-log.md`, or delete the sentence. Keep the first paragraph exactly this short: it is what passes the 30-second test.

---

## Project name
Night Shift

## Tagline (one line)
A skeleton crew of AI agents that ships while your team sleeps, built with Kiro Crew and Kiro CLI.

## The 30-second version (top of the description)

**What:** You write one paragraph of intent before you log off. Overnight, Kiro agents turn it into a spec, build it in parallel, prove it with property-based tests, and a rulebook decides what is safe to merge. In the morning a ghost hands you one page: what shipped, what needs you, and what it cost.

**Who:** Small teams and solo maintainers with more backlog than hours, and enterprises piloting AI-first delivery.

**Why it matters:** Agents are fast but still need babysitting. Night Shift makes intent explicit, checks correctness automatically, and only wakes a human for real decisions. Then it measures how often that was: [MEASURED: X% of tasks shipped with zero human touches over N nights].

## Inspiration
Kiro's frontier-teams guide describes teams that feed agents a backlog, run them overnight and review in the morning. We wanted that operating model as something you can clone: not a slide, a repo.

## What it does
- **Spec Gate:** vague or untestable requirements never reach a builder; they go to a question queue with a recommended default.
- **Night Conductor:** a Kiro Crew job runs headless Kiro CLI workers in parallel git worktrees under a credit budget.
- **Correctness gate:** property-based tests derived from EARS requirements, plus tests and scans; failures loop back to the agent.
- **Policy engine:** deterministic code, not an agent, decides merge or escalate. Risk can only go up as signals are added, and property tests prove it.
- **Morning briefing:** one page from a friendly ghost: merged, waiting for you, questions, spend, Human Touch Index.
- **Two apps from one skeleton:** *Lazarus* resurrects a 2003 Perl CGI bulletin board with proof of equivalent behaviour; *Chimera* is a spreadsheet whose cells are formulas, shell pipelines or HTTP calls.

## How we built it (Kiro features, named)
- **Kiro Crew:** bots (intake, pipeline health, docs sync, cost governor, morning briefing), conductor mode, schedules, memory.
- **Kiro CLI:** headless workers with scoped tool trust; custom agents; workflows.
- **Kiro IDE:** specs, steering, hooks; spec property-based tests.
- **Kiro Web:** spec mode and scheduled tasks that open PRs.
- **Specs:** EARS requirements tagged `[PBT]` or `[EX]`; brownfield specs for Lazarus.
- **Steering:** org rules plus per-role "must not" files. [MEASURED: steering ablation result]
- **Hooks:** spec gate, scope guard, test on save, touch logger, gate on stop. [MEASURED: hooks on vs off]
- **Custom agents:** eight least-privilege roles. [MEASURED: default vs role agent]
- **MCP:** `nightshift-mcp` (shared queue, ledger, policy across every surface) and `legacy-oracle-mcp` (ask the real legacy app). [MEASURED: oracle vs no oracle]
- **Property-based testing:** [MEASURED: bugs caught by PBT that unit tests missed]
- **Powers:** our own `night-shift` power; [MEASURED: which third-party powers we kept and why]

Full write-up with evidence: `docs/WRITEUP.md`.

## Challenges
[FILL from the log: e.g. headless permissions, first-night failure rate, credit budgeting]

## Accomplishments
[FILL: the one number you are proudest of, measured]

## What we learned
[FILL: the biggest surprise from the experiments]

## What's next (outlives the hackathon)
- The skeleton and the eight build labs are open source (MIT) and documented on the project site, so any team can adopt the model.
- Packaged as a Kiro power for one-step install.
- More apps on the same skeleton: overnight on-call, spec drift watch, docs that test their own code samples.

## Built With
`kiro` · `kiro-cli` · `kiro-crew` · `kiro-ide` · `kiro-web` · `kiro-specs` · `kiro-hooks` · `kiro-steering` · `kiro-powers` · `mcp` · `python` · `hypothesis` · `property-based-testing` · `perl` · `typescript` · `github-actions` · `github-pages`

## Links
- Repo: https://github.com/akashtalole/Kiroween2026
- Site: https://akashtalole.github.io/Kiroween2026/
- Video: [YouTube URL]
- Kiro Crew app repo (bonus): [URL]
- Blog post (bonus): [URL]
- Social post with #KiroweenHackathon26 (bonus): [URL]

---

## How this answers each judge

| Judge's ask | Where Night Shift answers it |
|---|---|
| **Vivek Velso:** "solves a real problem and makes me think 'I wouldn't have imagined building this before Kiro'" | The whole org is built from Kiro primitives that did not exist together before: Crew bots and schedules driving headless CLI workers, specs with property tests as the merge gate, hooks as org rules. The video says this out loud at 0:15. |
| **Floor Mesters:** "Scare me, then make it easy... a ghost that guides me or an error message that makes me laugh" | The morning briefing is delivered by a guide ghost that always ends with the one next action. Errors are funny and specific ("This spec is too vague to haunt anyone. Add an acceptance criterion like…"). See `docs/NIGHT_SHIFT.md`, section 16. |
| **Sameer Ali:** "things that outlive the hackathon... open-source tools, resources for learners" | MIT-licensed skeleton, eight public build labs, a 45-idea bank and a tested example on the project site. |

## Checklist before pressing Submit
- [ ] `bash tools/presubmit-check.sh` passes
- [ ] Category: **Skeleton Crew**; bonus prizes ticked only where eligible
- [ ] Kiro named in the description **and** in Built With
- [ ] Video public, under 3:00, shows a spec, a hook or steering on screen
- [ ] Judge credentials (if any) only in the private field
- [ ] Every `[MEASURED]` and `[FILL]` replaced or removed
