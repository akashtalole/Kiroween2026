---
inclusion: fileMatch
fileMatchPattern: ["**/test_*.py", "**/*_test.py", "**/*.test.ts", "tests/**", "**/tests/**"]
---
# Testing rules

**Rule.** Every acceptance criterion tagged `[PBT]` gets a property-based test. `[EX]` criteria get example tests.
*Why:* examples only cover the cases the author imagined; properties search the input space.

**Do**
```python
@given(changes)
def test_failed_gates_never_merge(c):
    if not c.gates_passed:
        assert decide(c) == "reject"
```
**Don't:** make `assert decide(Change(gates_passed=False)) == "reject"` the only test for a universal rule.

**Definition of done**
- [ ] each `[PBT]` criterion has a property named after its requirement ID in a comment
- [ ] Hypothesis seeds are printed on failure (default behaviour; do not suppress)
- [ ] no test deleted, skipped or weakened to get green
- [ ] a property that fails gets its counterexample recorded in `docs/pbt-catches.md`
