# Necromancer — Kiroween 2026 Plan

> **Raise dead open-source repos, with proof they still behave the same.**
> Category: **Resurrection** · Dates: build window Oct 30 – Dec 4, 2026 (deadline Dec 4, 2:00 pm PT)

Status of this doc: planning draft, 2026-11-05. Nothing here is built yet.

---

## 0. Do this week (blocking items)

| # | Action | Deadline |
|---|--------|----------|
| 1 | Create/confirm a Kiro account, note your **Kiro user ID or AWS account ID** | now |
| 2 | Submit the **Credit Request Form** (Devpost → Resources tab). 4,000 credits per team member, review takes ~48 business hours | **Dec 1, 12:00 pm PT** (do it by Nov 7) |
| 3 | Join the Devpost hackathon and the Kiro Discord (#kiroween-hackathon) | now |
| 4 | Decide team (max 3) and whether Student / Startup bonuses apply | Nov 7 |
| 5 | Register for Devpost Build Session (Nov 11, 10:00 am PT) | optional |

Credit form project blurb (paste-ready):
> Necromancer revives abandoned open-source libraries. It turns a dead repo's open issues into Kiro specs, upgrades its dependencies and build, and uses differential property-based testing to prove the revived version behaves like the original. Category: Resurrection.

---

## 1. Rules that shape the design

- Must be a **working app built with Kiro** (IDE / CLI / Web / Crew), **new code started on or after Oct 30**.
- Public **GitHub repo**, OSI license visible in About (we already have `LICENSE`), and a **`/.kiro` directory committed** (never in `.gitignore`).
- Demo video **< 3 min**, public on YouTube, showing the app working on its target device. No copyrighted music or third-party trademarks.
- A working app URL (or instructions), plus a **write-up of how Kiro was used** (IDE vs CLI vs Crew, custom agents, hooks, specs vs vibe coding, steering, MCP, PBT, powers).
- Scoring, equal weights (20% each): **Impact, Technological Implementation (depth of Kiro use), Design, Innovation, Presentation**. Stage 1 is pass/fail on theme fit and use of Kiro.
- Prize logic: one Overall **or** one Category prize (not both) plus any number of bonuses.

Implication: every Kiro feature we use needs to be **visible in the repo and the video**, not just claimed.

---

## 2. Product definition

**Problem.** Thousands of useful libraries are abandoned: broken builds on modern runtimes, CVEs in pinned dependencies, unmerged PRs. Forking and fixing is tedious and, worse, unverifiable: nobody trusts that the revived fork still does the same thing.

**Solution.** Necromancer runs a repeatable ritual and ends with evidence, not a vibe:

1. **Exhume**: fetch repo, metadata, open issues and PRs, CI status, dependency manifest (GitHub API).
2. **Autopsy**: build and test on a current toolchain in a sandbox; classify the *cause of death* (dead dependency, removed stdlib API, broken packaging, CVEs via OSV.dev).
3. **Séance**: cluster issues and PRs into **Kiro-style specs** (`requirements.md` in EARS form, `design.md`, `tasks.md`) so the revival is spec-driven.
4. **Reanimate**: execute tasks in the sandbox (dependency upgrades, packaging modernisation, API fixes), one commit per task.
5. **Proof of life**: **differential property-based tests**. Generate inputs from the public API's signatures and type hints; run old and new versions side by side; report parity. Divergences ("hauntings") are surfaced for a human to mark *intentional* or *regression*.
6. **Burial rites / certificate**: a resurrection report plus an auto-drafted PR or fork with the parity score.

**Audience.** Maintainers adopting orphaned projects, companies stuck on a dead dependency, security teams chasing unmaintained packages.

**Scope decision (important).** v1 supports **pure-Python libraries with a pytest suite** only. Hypothesis is mature and signature introspection is reliable. TS/JS (fast-check) is a stretch goal, not a promise.

### Judge-risk mitigations
- **Untrusted code execution on a public host is unsafe.** The hosted demo is a **replay mode** with pre-run resurrections of 3 real repos (full artifacts, parity graphs, diffs). Live mode runs locally via CLI/Docker and is documented in the README.
- **LLM cost and keys.** The deterministic pieces (autopsy, harness generation, parity runner) work without an LLM. The LLM is used for spec drafting and code fixes, and the cached demo runs need no key.
- **"Is it just a Dependabot clone?"** No: the differentiator is spec generation from the issue backlog plus differential PBT proof. Say this in the first 15 seconds of the video.

---

## 3. Architecture

> Full end-to-end design (journeys, pipeline, data contracts, APIs, sandbox, testing, build order): see [`docs/SOLUTION.md`](docs/SOLUTION.md).

```
necromancer/
├─ .kiro/                  # specs, steering, hooks, agents, MCP config (committed!)
├─ packages/
│  ├─ core/                # Python: exhume, autopsy, parity engine (Hypothesis)
│  ├─ sandbox/             # Docker runner, resource/network limits
│  ├─ mcp-server/          # necromancer-mcp: exposes exhume/autopsy/parity as MCP tools
│  └─ cli/                 # `necro exhume|autopsy|seance|raise|prove`
├─ apps/
│  └─ crypt/               # web UI (React + Vite), gothic dashboard
├─ demo/                   # 3 pre-run resurrection bundles (JSON + diffs + reports)
├─ docs/                   # write-up, architecture, Kiro usage log
├─ LICENSE
└─ README.md
```

Stack: Python 3.12 (core, FastAPI), Hypothesis, pytest, Docker, OSV.dev API, GitHub API; React + Vite + TypeScript for the UI. Hosted replay on a static host.

Key technical bet, **differential parity engine**:
- Build two isolated venvs (original at its last known-good env, revived at modern env).
- Discover public API: modules, functions, classes with signatures and type hints; fall back to docstring examples and existing tests as seeds.
- Generate strategies (`hypothesis.strategies.from_type`, `builds`) per callable; call both implementations with the same input in subprocess workers; compare return value, raised exception type, and (opt-in) side-effect snapshots.
- Output: per-function parity %, shrunk counterexamples for divergences, and flaky/nondeterministic detection (re-run to filter).

---

## 4. Kiro feature map (this is 20% of the score, plan it)

| Kiro feature | Concrete use in this project | Evidence for judges |
|---|---|---|
| **Specs** | 4 specs: `exhume-autopsy`, `seance-spec-gen`, `parity-engine`, `crypt-ui`. EARS requirements, design, tasks; build strictly task by task | `.kiro/specs/*`, short vibe-vs-spec comparison in write-up (build one small feature both ways and time it) |
| **Steering** | `product.md`, `tech.md`, `structure.md` plus custom `migration-rules.md` (what a safe upgrade is) and `pbt-guidelines.md` (how to write properties) | `.kiro/steering/*`; note which doc changed output quality most |
| **Hooks** | on-save: run affected tests; on-task-complete: update `docs/kiro-log.md`; pre-commit: secret scan; **parity gate**: block "done" if parity engine tests drop | `.kiro/hooks/*`, one hook shown firing in the video |
| **MCP** | GitHub MCP (issues/PRs), **our own `necromancer-mcp`** so Kiro can resurrect repos from chat (dogfooding), docs/search MCP for library docs | MCP config + a clip of Kiro calling our tool |
| **PBT** | Both the product's core and its own test suite; properties derived from spec requirements (e.g. "parity runner is symmetric", "shrinking terminates", "spec generator never drops an issue") | PBT section with a real bug PBT caught that unit tests missed (log these as they happen!) |
| **Custom agents** | `exhumer` (read-only investigation), `surgeon` (applies fixes, restricted scope), `reviewer` (checks diffs against steering) | `.kiro/agents/*`, notes on how scoping changed results |
| **Powers** | Install relevant powers from the Powers panel (testing, framework, Git workflow) and record what each changed | list in write-up; verify what is available in-app |
| **IDE vs CLI vs Crew** | IDE for specs and UI; CLI for batch runs and CI-style loops; Crew for the Best Kiro Crew App bonus: a crew (Coroner, Surgeon, Priest) running the ritual | one paragraph on differences in write-up; verify Crew's current capabilities before committing to it |

Habit: keep a running `docs/kiro-log.md` (date, feature used, what worked, what failed). The write-up is then assembly, not recall.

---

## 5. Timeline (Nov 5 → Dec 4)

**Week 1 (Nov 5–11): foundations**
- Credits requested, repo scaffold, `.kiro/` steering docs.
- Write spec 1 (exhume-autopsy) and spec 3 (parity-engine) first; they are the riskiest.
- **Spike (day 2–3): can we reliably get a parity score on one real dead library?** If not, narrow the API-discovery scope. Go/no-go checkpoint on Nov 10.
- Shortlist 3 demo targets (criteria below).

**Week 2 (Nov 12–18): the engine**
- Exhume, autopsy, sandbox, parity runner end to end via CLI on target #1.
- Hooks and PBT on the parity engine itself.
- `necromancer-mcp` v0.

**Week 3 (Nov 19–25): spec generation and UI**
- Séance: issue clustering to specs; Reanimate loop (task by task commits).
- Crypt UI: repo tombstone, autopsy report, spec view, parity "EKG", hauntings list.
- All 3 demo resurrections run and cached.

**Week 4 (Nov 26–Dec 1): polish and content**
- Design pass (accessibility: contrast, reduced motion, keyboard), README, Docker one-liner.
- Record demo, write Kiro write-up, **publish blog post** (Bonus Blog Prize) and **social post** with `#KiroweenHackathon26` at the start.
- Feature freeze **Nov 29**.

**Dec 2–3: submission**
- Fresh-clone test (judge's view), license/About check, `.kiro` not ignored, video public, Devpost form complete with bonus fields. **Submit Dec 3**, not Dec 4.

---

## 6. Demo targets (criteria, to be chosen in the Nov 10 spike)

A good target: pure Python, ≥ 50 stars, last commit ≥ 2 years ago, has pytest tests that fail or can't install on Python 3.12, has open issues/PRs, permissive license (so we can legally fork and demo), small enough to run in minutes. Choose one *easy* (clean win), one *medium* (some haunting divergences), one *hard* (honest partial result). Showing an honest divergence builds credibility.

---

## 7. Three-minute video script

| Time | Beat |
|---|---|
| 0:00–0:15 | Hook: "Millions of installs depend on code nobody maintains. We raise it from the dead and prove it still works." |
| 0:15–0:45 | Paste a dead repo URL → tombstone card, cause of death (build fails on 3.12, 2 CVEs) |
| 0:45–1:15 | Séance: open issues become a Kiro spec; show the tasks |
| 1:15–1:50 | Reanimate: tasks execute, commits appear |
| 1:50–2:25 | Proof of life: parity EKG, 97% parity, 3 hauntings with shrunk counterexamples; mark one intentional |
| 2:25–2:50 | Kiro under the hood: specs, hooks firing, MCP tool called from chat, a PBT-caught bug |
| 2:50–3:00 | Impact line and where to try it |

Show it running on the device it was built for; captions on; no copyrighted music.

---

## 8. Design direction (20% of score)

"The Crypt": dark, calm, readable. Spooky elements carry meaning: tombstone = repo card, EKG line = parity/health, candles = passing tasks, ghosts = hauntings. Avoid gimmicks that hurt usability: WCAG AA contrast, `prefers-reduced-motion`, keyboard navigable, no text in images.

---

## 9. Bonus prize stacking

| Bonus | Plan | Cost |
|---|---|---|
| Bonus Blog Prize (top 100, +2,000 credits) | Publish on dev.to/Hashnode/Medium during the period; mention Kiroween 2026 | ~3h |
| Social Blitz (5 winners) | Original, specific post with real learnings, starts with `#KiroweenHackathon26` | ~1h |
| Best Kiro Crew App ($1,000) | Wrap the ritual as a Crew app in its own public repo link | decide in week 3 |
| Best Demo ($1,000) | Needs top 10% overall + best Presentation score; invest in the video | already planned |
| Student / Startup / Ghost of Kiroween Past | Only if every condition is true for you; Ghost requires a 2025 registration and a *new* project | n/a unless eligible |

---

## 10. Risks and fallbacks

| Risk | Likelihood | Fallback |
|---|---|---|
| Parity engine can't auto-generate valid inputs for many APIs | High | Seed from existing tests and docstrings; report coverage honestly; restrict to functions with type hints |
| LLM upgrades introduce subtle breakage | Medium | That is exactly what parity tests catch. Show it as a feature |
| Sandbox/Docker issues | Medium | Local venv fallback with documented limits |
| Time overrun | High | Cut order: Crew bonus, then TS support, then live mode in UI. Never cut parity engine, the 3 cached demos, the video |
| Judges can't run it | Medium | Replay demo URL needing no login; README tested on a fresh clone |

---

## 11. Alternatives if we pivot (decide by Nov 10)

(Full idea bank with Kiro-feature showcase and ratings is in section 13.)

- **Teletext 2.0** (Resurrection): AI-summarised numbered pages for low-bandwidth users.
- **Séance** (Frankenstein): repo autopsy and "ask the dead codebase" tool.
- **Bones** (Skeleton Crew): spec-in-app-out template with two apps.
- **Ledger of the Dead** (Costume Contest): spooky budget tracker.

---

## 12. Open decisions

1. Confirm Necromancer, or pick another idea.
2. Solo or team (up to 3, each can request 4,000 credits)?
3. Student / Startup eligibility?
4. LLM provider and budget for live runs.
5. Python-only for v1: OK?

---

## 13. Expanded idea bank (each built to showcase Kiro)

Every idea lists the Kiro features it makes *visible*, since depth of Kiro use is 20% of the score. Ratings (1-5) are my judgment, not data: **Imp**act, **Inn**ovation, **Des**ign potential, **Risk** (higher = riskier), **Eff**ort (higher = more work, ~4 weeks solo).

### Resurrection

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| R1 | **Necromancer** | Revive dead OSS libs, prove parity with differential PBT | Specs from issue backlog, PBT, hooks, own MCP, custom agents | 5 | 5 | 3 | 4 | 5 |
| R2 | **Dead Letter Office** | Find rotten links in a repo or docs site, recover from Wayback or a semantically matching live page, open a PR | Hook: link-check on commit; MCP: Wayback + GitHub; PBT: "a fix never changes non-link text"; steering: citation rules | 4 | 4 | 3 | 2 | 2 |
| R3 | **NetNews 2.0** | Usenet reborn: NNTP-compatible newsgroups where humans and AI agents post, threads are queryable over MCP | MCP server as the product; spec for NNTP subset; PBT for threading/ordering invariants | 3 | 5 | 4 | 3 | 3 |
| R4 | **HyperCard Reborn** | Stacks of cards with a tiny scripting language; LLM turns plain English into card scripts | Spec-driven interpreter, PBT for the parser (round-trip: parse then print), steering for the DSL | 3 | 4 | 5 | 3 | 4 |
| R5 | **BBS Sysop** | Dial-up-style BBS with door games and an AI sysop, running in the browser | Vibe vs spec comparison is easy to showcase; hooks for content moderation tests | 2 | 3 | 5 | 1 | 2 |
| R6 | **Teletext 2.0** | Numbered pages of AI-summarised news, prices, results for 2G and SMS users | Steering for plain-language rules; MCP data sources; PBT for page-size limits | 4 | 4 | 4 | 2 | 3 |

### Frankenstein

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| F1 | **Séance** | Repo autopsy (git history + AST + logs + LLM) with a "ask the dead codebase" chat | Custom agents (coroner, historian), MCP over git, hooks | 4 | 4 | 4 | 2 | 3 |
| F2 | **Pipes & Cells** | A spreadsheet whose cells are shell pipelines and MCP tool calls; recalculation is a dataflow graph | Spec for the dependency graph, PBT for recalculation (order-independent, cycle-safe), MCP as cell functions | 3 | 5 | 4 | 3 | 4 |
| F3 | **Reanimated SQL** | Every row change is a git commit; query "as of" any time; branch and merge tables | PBT for merge invariants (commutativity where claimed), specs for the storage format | 3 | 5 | 2 | 4 | 4 |
| F4 | **Tarot Postmortem** | Incident review that stitches logs, alerts, chat export and a tarot-style narrative into a blameless timeline | Steering for blameless tone, hooks for PII scrubbing, MCP for log sources | 4 | 3 | 5 | 2 | 3 |

### Skeleton Crew (repo needs two separate app folders)

| # | Idea | Pitch | Two apps | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|----------|---------------|-----|-----|-----|------|-----|
| S1 | **Bones** | One spec generates data model, API, MCP server and UI | Clinic queue; haunted-house booking | Specs *are* the framework; steering as template rules | 4 | 4 | 3 | 3 | 4 |
| S2 | **Ribcage** | Template for production-grade MCP servers: auth, rate limits, tests, PBT harness, docs | Library-lending MCP; tabletop-RPG campaign MCP | MCP, PBT, hooks, powers; easy to prove versatility | 4 | 3 | 2 | 2 | 3 |
| S3 | **Marrow** | Local-first, offline-sync skeleton with CRDTs | Shared grocery list; field-inspection forms | PBT for CRDT convergence (a natural fit), specs | 4 | 4 | 3 | 4 | 4 |

### Costume Contest

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| C1 | **Ledger of the Dead** | Budget/habit tracker where ghosts represent unpaid bills and abandoned goals | Steering for design tokens and a11y; hook for contrast checks | 3 | 3 | 5 | 1 | 2 |
| C2 | **Spirit Board Flashcards** | Spaced repetition where forgotten cards become ghosts you re-bind by recall | PBT for the scheduler (intervals monotonic, no card lost), design steering | 4 | 3 | 5 | 1 | 2 |
| C3 | **Haunted On-Call** | Incident triage dashboard: alerts as apparitions, runbooks as exorcisms | MCP for alert sources, hooks, specs for severity logic | 4 | 3 | 5 | 2 | 3 |

### Startup angle ($10k Best Startup Project, founders only)

- **Necro.dev**: maintained-fork-as-a-service for orphaned dependencies (sell to companies stuck on a dead lib). Needs LinkedIn plus a startup website in the submission.
- **Dead Letter Office as a GitHub App**: recurring link-health monitoring for docs teams.

### Kiro Crew bonus ($1,000)

Any pipeline with distinct roles fits: Necromancer as a crew (**Coroner** diagnoses, **Surgeon** patches, **Priest** verifies parity, **Gravedigger** cleans up), or Dead Letter Office as (**Finder**, **Archivist**, **Editor**). Check Crew's current capabilities before committing.

### How I'd choose

- **Highest ceiling:** R1 Necromancer.
- **Best hedge (low risk, still strong):** R2 Dead Letter Office. It shares the Resurrection category, reuses the same Kiro story (hooks, MCP, PBT), and could ship in about a week. Build it first as a warm-up or fallback.
- **Strongest pure Kiro-depth story:** S2 Ribcage (MCP + PBT + powers) or S3 Marrow (PBT on CRDTs).
- **Best design play:** C2 Spirit Board Flashcards.

### Combine for more Kiro depth

Ship **one flagship plus one small sibling in the same repo family**, for example Necromancer plus Dead Letter Office sharing the `necromancer-mcp` server. This does not enter two categories (each submission has one), but it makes the Kiro write-up richer: one reusable MCP, two specs families, shared steering.

### Verify before committing to any idea
- Search Devpost's Kiroween 2025 gallery and GitHub for near-duplicates (innovation score).
- Confirm every external API (Wayback, OSV, GitHub) has usable rate limits for a live demo.
- Confirm trademark safety: no real brand names or assets (e.g. skip Clippy/Winamp-style references).

---

## 14. Idea bank, round 2 (new angles)

Same rating scale as section 13 (1-5, my judgment; Risk and Effort: higher is worse). This round adds three groups: **legacy and data rescue** (strong real-world impact), **Kiro-native tools** (the judges are the Kiro team, and tools that improve Kiro workflows score well on Technological Implementation), and **design and accessibility plays**.

### Resurrection: legacy and data rescue

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| R7 | **Rosetta Crypt** | Translate legacy COBOL/Fortran/Pascal routines to modern Python or TS, and *prove* equivalence with differential property-based tests (reuses the Necromancer parity engine) | Specs per routine, PBT is the product, hooks run proof on every translated unit, MCP for a reference interpreter | 5 | 4 | 3 | 4 | 4 |
| R8 | **Format Morgue** | Revive obsolete file formats (old word processors, spreadsheets, image formats) with spec-driven converters; round-trip properties verify no data loss | Spec per format from public documentation, PBT round-trip (`decode(encode(x)) == x`), steering for byte-level rules | 4 | 4 | 3 | 3 | 3 |
| R9 | **Afterlife** | Rescue your data from shut-down services: import a user's own export archives into open formats (OPML, Markdown, JSON, ICS) with a verified completeness report | Specs per service archive format, PBT for "no item lost", hooks scrubbing sample data, MCP to query the rescued archive | 5 | 3 | 4 | 2 | 3 |
| R10 | **Revive a Language** | Community dictionary and spaced-repetition app for an endangered language, with audio and example sentences supplied by speakers | Steering for consent and attribution rules, specs for dataset provenance, PBT for the scheduler | 5 | 3 | 4 | 4 | 4 |

Notes:
- R7 is Necromancer's sibling, not a separate engine: it swaps "upgrade a library" for "translate a routine" while reusing the parity proof. Its main risk is a trustworthy reference implementation of the legacy language; limit to a small subset with an existing open-source interpreter.
- R9 must only process archives *the user supplies* and must be built from public format documentation and synthetic sample files. No scraping, no credentials.
- R10 needs real community involvement to be credible; treat it as high-risk unless you already have a partner. Never fabricate language data.

### Frankenstein

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| F5 | **Spectral Shell** | Voice-controlled terminal for developers with limited mobility: speech recognition + shell + intent parsing, with a safety layer that always confirms destructive commands | Steering with a command risk taxonomy, PBT on the safety classifier (no destructive command passes unconfirmed), hooks, MCP for shell tools | 5 | 4 | 4 | 3 | 3 |
| F6 | **Spec Autopsy** | A linter and analyser for Kiro specs: EARS validity, requirement-to-task traceability, orphan tasks, vague words; drafts PBT properties from acceptance criteria | Dogfoods specs and PBT, ships as an MCP server and a Kiro hook, easy to demonstrate | 4 | 4 | 3 | 2 | 3 |

### Kiro-native tools (judged by the people who build Kiro)

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| K1 | **Steering Lab** | An A/B harness that answers "does this steering doc actually change Kiro's output?": run the same task with and without a steering file, score the diffs against a rubric | Steering is the subject; CLI for batch runs, custom agents as graders, evidence in the write-up | 4 | 4 | 3 | 3 | 3 |
| K2 | **Spec Archaeology** | Reverse-engineer specs from legacy behaviour: record an app's observable behaviour (API traffic, CLI sessions), cluster it, and emit EARS requirements plus property tests | Reverse of the normal spec flow; strong startup story for legacy modernisation | 5 | 5 | 3 | 4 | 4 |
| K3 | **A Kiro Power** | Package a focused, high-quality Power (bundled MCP tools + steering + docs), for example accessibility auditing or API-contract checking, and show it improving a real build | Power authoring is the whole story; verify the packaging format in the app first | 3 | 3 | 2 | 2 | 2 |

### Skeleton Crew

| # | Idea | Pitch | Two apps | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|----------|---------------|-----|-----|-----|------|-----|
| S4 | **Vertebrae** | Minimal evaluation-harness skeleton for LLM apps: datasets, graders, regression gates, a report page | Support-bot evaluator; code-review-agent evaluator | PBT for grader consistency, specs for the harness contract, hooks as regression gates | 4 | 3 | 3 | 2 | 3 |
| S5 | **Hexa-Core** | One domain core with three thin front ends (CLI, web, chat bot) generated from a spec | Habit tracker; shared-expense splitter | Spec to ports/adapters, steering for architecture rules | 3 | 3 | 3 | 2 | 3 |

### Costume Contest

| # | Idea | Pitch | Kiro showcase | Imp | Inn | Des | Risk | Eff |
|---|------|-------|---------------|-----|-----|-----|------|-----|
| C4 | **Ghost Cartographer** | Map of local legends and folklore from open datasets and contributed stories, with a haunted-map UI (fog, flickering lanterns) | Steering for design tokens and contrast, hook for a11y checks, specs for the map data model | 2 | 3 | 5 | 1 | 2 |
| C5 | **Mourning Reader** | Distraction-free reading app where text "materialises" line by line, dyslexia-friendly typography, reduced-motion safe | Design steering, PBT for pagination (no text lost or duplicated), a11y hooks | 3 | 3 | 5 | 1 | 2 |

### Round-2 observations

- **Highest-impact new ideas:** R9 Afterlife and R7 Rosetta Crypt. Both are about real losses (data, legacy knowledge) and both have an objective completeness or equivalence check.
- **Most Kiro-native:** K2 Spec Archaeology and F6 Spec Autopsy. They turn Kiro's own concepts (specs, PBT) into the product, which makes the "deep understanding of Kiro features" criterion easy to demonstrate.
- **Best synergy with the existing plan:** R7 and K2 both reuse the Necromancer parity and characterization machinery (see `docs/ADVANCED_FEATURES.md`, A1). If you build the engine once, you can show it as a pipeline with two front doors.
- **Lowest risk:** R9, C4, C5, K3.
- **Watch-outs:** innovation scoring penalises ideas that resemble existing tools; check Kiroween 2025 submissions and GitHub before committing. Avoid any real service logos, brand names or proprietary file samples.

### Timing reality check (as of Nov 13)

About 21 days remain until Dec 4 and no idea is locked. The Nov 10 spike gate in section 5 has passed unexecuted, so treat the schedule as compressed:

| Window | Goal |
|---|---|
| Nov 13-15 | **Decide the idea.** Request Kiro credits (deadline Dec 1, review ~48 business hours, so do it today). Check for near-duplicates |
| Nov 16-20 | Scaffold, steering, first spec, core engine spike with go/no-go on Nov 20 |
| Nov 21-27 | Core features plus one advanced feature; design pass; feature freeze Nov 29 |
| Nov 28-Dec 3 | Demo bundles, video, write-up, blog and social posts, submit Dec 3 |

If the engine-heavy ideas (R1, R7, K2) feel too big for three weeks, the lower-effort picks above (R2 Dead Letter Office, R9 Afterlife, K3 Power, S4 Vertebrae) still compete well when the Kiro usage is deep and the demo is clean.
