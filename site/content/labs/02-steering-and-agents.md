# Lab 02 · Steering and role agents

**Goal:** give every agent the same org context, then narrow each role to the tools it needs. Experiments **E5** (steering ablation) and **E2** (agent A/B).

## 1. Layout

```text
.kiro/
├─ steering/
│  ├─ product.md  tech.md  structure.md        # what, with what, where
│  ├─ security.md  testing.md  release.md       # org golden rules
│  └─ roles/builder-must-not.md  reviewer-must-not.md
└─ agents/
   ├─ analyst.json  architect.json  builder.json  tester.json
   └─ reviewer.json  security.json  scribe.json  release.json
```

## 2. A steering file that works: rule, why, example, anti-pattern

```markdown
# Testing rules

**Rule.** Every requirement tagged `[PBT]` gets a property test; never only an example test.

**Why.** Examples only cover cases the author imagined. Properties found real bugs in our policy engine.

**Do**
\`\`\`python
@given(changes)
def test_failed_gates_never_merge(c):
    if not c.gates_passed:
        assert decide(c) == "reject"
\`\`\`

**Don't.** `assert decide(Change(gates_passed=False)) == "reject"` as the only test.

**Definition of done**
- [ ] each `[PBT]` criterion has a property
- [ ] seeds are logged on failure
- [ ] no test deleted or skipped to get green
```

*Verify whether your Kiro version supports conditional steering inclusion (always, file-matched, manual) and use it to keep context small.*

## 3. A least-privilege custom agent

Custom agents live in `.kiro/agents/` as JSON or Markdown, with the same fields. The documented fields include `name`, `description`, `tools`, `excludedTools`, `includeMcpJson`, `includePowers` and `resources`.

```json
{
  "name": "builder",
  "description": "Implements exactly one task from tasks.md inside its own worktree.",
  "tools": ["read", "write", "shell"],
  "excludedTools": ["knowledge"],
  "includeMcpJson": false,
  "includePowers": false,
  "resources": [
    "file://./.kiro/steering/tech.md",
    "file://./.kiro/steering/testing.md",
    "file://./.kiro/steering/roles/builder-must-not.md"
  ]
}
```

Keep a `reviewer` that is **read-only** and never shares a session with the builder, so it judges the result without inheriting the builder's reasoning.

## 4. Experiment E5: steering ablation

Run the same five tasks under three conditions: **(a)** no steering, **(b)** terse rules, **(c)** rich steering (rule + why + example + anti-pattern + checklist). Score each output against a fixed rubric: convention violations, missing tests, wrong libraries, security-rule breaches. Log the table in `docs/steering-ablation.md`. State which condition won *as measured*.

## 5. Experiment E2: agent A/B

Same five tasks with the default agent, then with `builder`. Compare permission prompts, out-of-scope edits, retries to green and credits.

## Checkpoint

- [ ] Steering layers committed
- [ ] Eight role agents committed
- [ ] E5 and E2 logged, including any result that showed no difference
