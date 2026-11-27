---
inclusion: always
---
# Structure

```
.kiro/            steering, agents, skills, hooks, specs   (never gitignored)
org/              nightshift.yaml: roles, gates, autonomy tiers, budgets
tools/            worker runner, gates, ledger, hook scripts
examples/         tested reference code (policy engine)
apps/lazarus/     Resurrection app (legacy/ is the 2003 Perl app; modern/ is the rewrite)
apps/chimera/     Frankenstein app
crew/             Kiro Crew bot charters and schedules
site/             project site (GitHub Pages)
docs/             design, plans, write-up, evidence log
tests/            tests for tools/ and hook scripts
ledger.ndjson     append-only event log (gitignored locally, sample committed in docs/)
```

New code goes next to its tests. One spec per capability under `.kiro/specs/<capability>/`.
