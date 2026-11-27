---
inclusion: auto
name: release
description: Merge, release and evidence-pack rules. Use when preparing a pull request, deciding whether a change can merge, or writing an evidence pack.
---
# Release rules

- A change can merge without a human only when the policy engine says `merge` (tiers A0 or A1, all gates green, two independent reviews for A1).
- Every PR carries an evidence pack: requirement IDs, gate results, property-test seeds, review verdicts, policy decision and the signals behind it, credits used, and any human touches.
- Kiro Web never merges on its own; in this project, merges happen only in demo repositories, through the policy engine.
- Commit messages: `ns(<task-id>): <summary> [R-...]`.
