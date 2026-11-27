---
name: policy-check
description: Classify a change into risk tier A0-A3 and decide merge, queue_for_human or reject using the deterministic Night Shift policy engine. Use before any merge decision or when asked whether a change is safe to auto-merge.
---
# Policy check

The merge decision is made by code, not by an agent. Run it on the current diff:

```bash
python3 .kiro/skills/policy-check/scripts/policy_check.py --base origin/main --gates-passed yes --reviews 2
```

Flags: `--public-api-changed` and `--deps-changed` when those apply (the script also detects dependency-file changes itself). It prints JSON: `tier`, `decision`, and `signals` (why).

Rules you must follow:
- Report the decision exactly as printed. Never argue it down.
- If the decision is `queue_for_human`, name the signal that raised the tier in one sentence.
- Tiers only go up: adding files, lines, API or dependency changes can never lower the tier (this is property-tested in `examples/policy-engine`).
