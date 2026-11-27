---
name: touch-index
description: Compute the Human Touch Index and other Night Shift metrics from ledger.ndjson. Use when asked how autonomous a night was, for the morning briefing, or for the write-up numbers.
---
# Human Touch Index

```bash
python3 .kiro/skills/touch-index/scripts/touch_index.py ledger.ndjson            # human-readable
python3 .kiro/skills/touch-index/scripts/touch_index.py ledger.ndjson --json     # for dashboards
python3 .kiro/skills/touch-index/scripts/touch_index.py ledger.ndjson --night 2026-11-28
```

Ledger events (one JSON object per line) the script understands:
- `{"type":"task_done","task":"T1","merged":true,"retries":1,"credits":12.5,"night":"2026-11-28"}`
- `{"type":"human_prompt","task":"T1","seconds":40,"night":"2026-11-28"}` (from the touch-logger hook)
- `{"type":"human_approval","task":"T2","seconds":90,"night":"2026-11-28"}`
- `{"type":"escape","task":"T1","night":"2026-11-29"}` (a defect found after merge)

Report numbers exactly as computed. Never round a bad night into a good one.
