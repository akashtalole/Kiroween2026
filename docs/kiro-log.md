# Kiro evidence log

One entry per experiment or notable event, written the same day. `docs/WRITEUP.md` may only cite what is here.

## 2026-11-27 Setup: initial .kiro configuration drafted
Surface: none yet (drafted outside Kiro, in a Claude Code session)
What: first versions of steering (6 files), role agents (8), skills (5, with tested scripts), hooks (7; 2 disabled until trigger names are verified), spec templates, Crew bot charters (6).
Next: load each in Kiro IDE and CLI, fix anything Kiro rejects, and record what changed here. Specs themselves are to be created in Kiro.
Evidence: commit history; `python3 -m pytest -q tests examples/policy-engine` (25 passed).

<!-- template
## <date> E<n>: <title>
Surface: IDE|CLI|Web|Crew     Agent: <name>
Setup: <conditions A/B>
Metrics: time=<..> credits=<..> human_msgs=<..> prompts=<..> retries=<..> defects=<..>
Result: <one paragraph>
Evidence: <paths / links>
Surprise: <what you did not expect>
-->
