# Lab 04 · Specs with EARS and property tags

**Goal:** structure each spec so Kiro can derive tests from it. Experiment **E4**: the same feature built by spec and by vibe coding.

## 1. Why this shape

Kiro turns a prompt into requirements with acceptance criteria, a design and sequenced tasks. Its property-based testing extracts properties from EARS-formatted requirements, then generates many random cases. That feature runs **in the IDE only**, so author specs and run spec-level property tests there. Hypothesis and fast-check tests still run anywhere.

## 2. Requirements template

```markdown
# Requirements: Autonomy policy

## R-POL-1 Tier classification
**User story.** As a release owner, I want each change classified into a risk tier so that only low-risk changes merge without a human.

Acceptance criteria
1. [PBT] WHEN a change is classified, THE system SHALL return exactly one of A0, A1, A2, A3.
2. [PBT] WHEN any signal is added to a change (a file, lines, an API or dependency change), THE tier SHALL NOT decrease.
3. [PBT] WHEN a change touches an auth, secrets, infra or migrations path, THE tier SHALL be A3.
4. [EX]  WHEN the policy file is missing, THE system SHALL refuse to merge and report why.

## R-POL-2 Merge decision
1. [PBT] IF any gate failed, THEN THE system SHALL reject.
2. [PBT] IF the tier is A2 or A3, THEN THE system SHALL NOT merge automatically.
```

`[PBT]` marks universal statements. `[EX]` marks cases better covered by examples (UI, external services, non-determinism).

## 3. Design file: correctness properties

```markdown
## Correctness properties
| ID | Property | Requirement |
|---|---|---|
| P1 | classify returns one of four tiers | R-POL-1.1 |
| P2 | tier is monotonic in added signals | R-POL-1.2 |
| P3 | gate failure implies reject | R-POL-2.1 |
| P4 | A2/A3 never auto-merge | R-POL-2.2 |
```

## 4. Tasks file

Each task names the requirement IDs it satisfies and the test that proves it. PBT tasks for `[PBT]` criteria are **not optional** (Kiro makes PBTs optional by default so you can focus on the core first; override that for these).

```markdown
- [ ] 1. Implement classify and decide  (R-POL-1.1, 1.3, R-POL-2.1, 2.2)
- [ ] 2. Property test: monotonic tier   (P2)  ← must pass before task 3
- [ ] 3. Property test: reject on failed gates (P3)
```

## 5. Brownfield variant (Lazarus)

For the legacy app, ask Kiro to analyse the codebase and generate specs **for what exists**, then correct them using the live legacy oracle (Lab 06). The requirement says what the legacy system *does*, not what it should do.

## 6. Experiment E4: spec vs vibe

Implement "a dependency change raises the tier to at least A2" twice on separate branches: **A**, chat prompts only; **B**, spec first. Record prompts used, rework cycles, bugs found later by property tests, and time. Publish both summaries.

## Checkpoint

- [ ] Four specs with `[PBT]` / `[EX]` tags
- [ ] IDE spec property tests run on at least three specs
- [ ] E4 logged
