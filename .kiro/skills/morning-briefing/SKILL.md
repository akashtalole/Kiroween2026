---
name: morning-briefing
description: Write Night Shift's one-page morning briefing from the ledger, evidence packs and question queue, in the guide ghost's voice. Use for the scheduled 07:00 briefing or when someone asks what happened overnight.
---
# Morning briefing

1. Compute numbers with the touch-index skill for last night (`--night <date> --json`).
2. Read `evidence/*.md` changed since last night and the open questions in `.kiro/specs/*/requirements.md`.
3. Write `docs/briefings/<date>.md` with **at most** these sections:

```markdown
# 👻 While you slept (<date>)
**<one playful line that is also true>** e.g. "Quiet night. 7 shipped, nobody screamed."
## Needs you (do these first)
- [ ] <item>: <why it waits, one sentence> → <the one action to take>
## Shipped
- <task>: <one line> (tier, evidence link)
## Questions I parked
- <question> · my default if you don't answer by tonight: <default>
## Numbers
zero-touch rate · touches per task · retries per task · credits · escapes
```

House style: spooky is welcome, confusing is not. Every item ends with one clear next action. Never joke about lost work, security problems or spending; state those plainly first. Never invent a number.
