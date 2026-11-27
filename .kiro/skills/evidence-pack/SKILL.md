---
name: evidence-pack
description: Write the evidence pack for a finished Night Shift task so a human can decide in two minutes without reading the code. Use when a task is done, before asking the policy engine for a decision, or when preparing a pull request description.
---
# Evidence pack

Write `evidence/<task-id>.md` with exactly these sections, in this order. Use only facts you can point to; write "not run" rather than guessing.

```markdown
# Evidence: <task-id> <one-line summary>
## Requirements
R-... (link to .kiro/specs/<capability>/requirements.md), one line each on how it is satisfied
## Gates
| Gate | Result | Detail |
| unit tests | pass/fail/not run | count |
| property tests | pass/fail/not run | properties, seeds on failure |
| lint | ... | ... |
| secret scan | ... | ... |
## Reviews
reviewer: approve/request-changes (key points) · security: ...
## Policy decision
paste the JSON from the policy-check skill
## Cost and touches
credits: N · retries: N · human touches: N (from ledger.ndjson)
## What a human should look at
the one or two things that matter, or "nothing: tier A0/A1, all green"
```
