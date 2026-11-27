# What property-based and mutation testing caught

Real findings only, newest first. Each entry: what was measured, what it found, what changed.

## 2026-11-27 Policy engine: the properties checked shape, not rules (mutation testing)
- **Tool:** `tools/frontier/mutate.py examples/policy-engine/policy.py examples/policy-engine/test_policy.py`
- **Before:** the 5 original properties (monotonic tier, determinism, failed gates reject, A2/A3 never auto-merge) killed **10 of 34** mutants (0.29). Deleting A3 globs, moving the 250-line threshold, swapping `max`/`min` or `and`/`or` all survived. The properties described the *shape* of the policy but not its *rules*.
- **Real bug found while writing the missing properties:** `**/*.md` does not match a root-level `README.md` (fnmatch needs a `/`), so a README-only change was classified **A1** instead of **A0**. Fixed by adding `*.md` to `A0_PATHS`.
- **After:** 8 rule properties added (A3 paths always A3; docs/tests-only small changes are A0 and merge; exact 250/251 boundary; API or dependency change is at least A2, and exactly A2 on ordinary code; A1 needs two reviews; empty change is A0). **32 of 35** mutants killed (0.91).
- **Remaining survivors are equivalent mutants:** `**/*.md` is now redundant with `*.md`; two dataclass default values are never relied on by the tests.
- **Also found:** a bug in the mutation tool itself. Tests left beside the original module imported it instead of the mutant, so the first run scored 0/34. Fixed by copying the tests next to the mutant.
