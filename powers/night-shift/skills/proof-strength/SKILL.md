---
name: proof-strength
description: Measure how strong a test suite really is by planting small bugs (mutation testing) and counting how many the tests catch. Use when asked whether tests or property-based tests are good enough, or before trusting an auto-merge gate.
---
# Proof strength

```bash
python3 scripts/mutate.py <module.py> <test file or folder>          # human-readable
python3 scripts/mutate.py <module.py> <test file or folder> --json   # for dashboards
```

Report the score (killed / total) and list every surviving mutant. For each survivor, either write the property or example that would catch it, or explain why it is an equivalent mutant (the code behaves the same). A high pass rate with a low proof strength means the tests check shape, not rules.
