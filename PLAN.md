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
