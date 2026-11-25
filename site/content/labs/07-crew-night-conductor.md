# Lab 07 · Crew bots and the Night Conductor

**Goal:** run the pipeline in parallel while you sleep, and wake up to a one-page briefing.

> Crew bots, scheduled jobs and conductor mode are documented features; the exact configuration screens differ by version. Treat the steps below as the design and confirm each setting in the app.

## 1. The three Crew building blocks

| Mode | Use for | Remembers |
|---|---|---|
| Session | one ad hoc task | global memory |
| Conductor mode | a goal with many tasks; the chat agent coordinates worker sessions | memory plus a goal ledger |
| Bot | ongoing ownership with no end date | its own memory and limits |

Night Shift uses **conductor mode** for the nightly goal and **bots** for the always-on roles.

## 2. Worker runner (starting point, not yet run)

Each task runs in its own git worktree with a headless, scoped Kiro CLI session:

```bash
#!/usr/bin/env bash
# tools/run_task.sh <task-id> <agent>
set -euo pipefail
TASK="$1"; AGENT="${2:-builder}"
git worktree add "../wt-$TASK" -b "ns/$TASK" origin/main
cd "../wt-$TASK"
kiro-cli chat --v3 --no-interactive \
  --trust-tools=read_file,write_file,run_command \
  "Using the $AGENT role and the spec in .kiro/specs/$TASK, implement the next unchecked task. Run the tests. Stop when green or after 3 failed attempts."
python ../night-shift/tools/gates.py --task "$TASK"      # correctness gate
python ../night-shift/tools/evidence.py --task "$TASK"   # evidence pack
```

Run several in parallel with `xargs -P`:

```bash
cat tonight.txt | xargs -n1 -P4 -I{} tools/run_task.sh {} builder
```

Tool names for `--trust-tools` depend on the harness; check the headless docs for your version and prefer a scoped `permissions.yaml` over broad trust.

## 3. Scheduling

Crew accepts natural-language schedules. Examples in the documented style:

> "Every night at 22:00, run the Night Conductor over the top 4 spec-approved backlog items with a 400-credit cap."
> "Every weekday at 07:00, write the morning briefing: merged overnight, queued for me, open questions, spend, Human Touch Index."

Kiro Web also supports scheduled tasks that open PRs on a cron. It never merges on its own: in this project the **policy engine** merges, in demo repositories only.

## 4. Bots

| Bot | Trigger | Cannot |
|---|---|---|
| Intake | hourly or on new issue | merge, close issues |
| Pipeline health | every 30 minutes | deploy |
| Docs sync | on merge | change code |
| Cost governor | each run | start tasks |
| Morning briefing | weekday 07:00 | act on its own |

Teach one correction ("new endpoints need a property test") and check that a later task follows it; that tests Crew's memory.

## 5. Safety rails

- Per-night and per-task credit caps, plus a `nightshift pause` kill switch
- Treat issue text as **untrusted input**: the intake bot strips instructions and the spec is the contract
- No secrets in the repo; the secret-scan hook runs before commits

## Checkpoint

- [ ] One night run completes with a briefing
- [ ] First-night numbers recorded honestly (they will be worse than the third)
- [ ] Memory test logged
