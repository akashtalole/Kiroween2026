# Tasks: <capability>

Line syntax read by tools/frontier/task_dag.py and `nightshift plan`:
`- [ ] <n>. <title> (<requirement IDs>) (after <n>, <n>) (files: <path>, <path>)`
Tasks in one wave run in parallel worktrees; two tasks that list the same file never share a wave.

- [ ] 1. <smallest buildable step> (R-<AREA>-1.1) (files: src/<module>.py) · proven by: <test name>
- [ ] 2. Property test P1 (R-<AREA>-1.1) (after 1) (files: tests/test_<module>.py)
- [ ] 3. <independent step> (R-<AREA>-2.1) (files: src/<other>.py)
- [ ] 4. Docs (after 2, 3) (files: README.md)
