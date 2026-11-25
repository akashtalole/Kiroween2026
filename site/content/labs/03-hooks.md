# Lab 03 · Hooks that run the org

**Goal:** turn the rules into automation that fires without anyone remembering to. Experiment **E3** (hooks off vs on).

## 1. How hooks work

Hook files live in `.kiro/hooks/*.json`. Each defines a trigger, an optional `matcher` and an action. A **command** action runs a shell command in the project root and receives session context as JSON on stdin. An **agent** action injects a prompt into the conversation. The documented schema:

```json
{
  "version": "v1",
  "hooks": [
    {
      "name": "Test on save",
      "trigger": "PostFileSave",
      "matcher": "\\.(py|ts)$",
      "action": { "type": "command", "command": "python tools/run_affected_tests.py" }
    }
  ]
}
```

`PostFileSave` is the trigger name shown in the docs. **Verify the exact identifiers** for the others on the *Hook types* page before writing each file, and check which triggers run on which surface (file and task triggers: IDE and CLI V3; Kiro Web runs Prompt Submit, Agent Stop, Session Start, Pre Tool Use and Post Tool Use).

## 2. The eight hooks

| Hook | Trigger | Surfaces | Does |
|---|---|---|---|
| `test-on-save` | File Save | IDE, CLI V3 | tests for the saved file |
| `spec-gate` | Pre Task Execution | IDE, CLI V3 | lint requirements; park a task with a question if vague |
| `scope-guard` | Pre Tool Use | IDE, CLI, Web | block writes outside the role's allowed paths |
| `secret-scan` | Pre Tool Use or File Save | all | stop secrets entering commits |
| `gate-on-stop` | Agent Stop | IDE, CLI, Web | run the correctness gate; feed failures back |
| `ledger-on-task` | Post Task Execution | IDE, CLI V3 | append credits and retries to the ledger |
| `touch-logger` | Prompt Submit | IDE, CLI, Web | log every human prompt as a touch |
| `session-budget` | Session Start | IDE, CLI V3, Web | inject remaining credit budget |

Notes from the docs: CLI Prompt Submit hooks cannot block (logging is fine), and long CLI V3 hook output is saved to a file with the first part shown to the agent. Whether *Pre Task Execution* can block is something to verify; if not, run `spec-gate` at Agent Stop and in CI.

## 3. A touch logger (starting point, not yet run)

```python
# tools/touch_logger.py: reads hook JSON on stdin, appends one ledger line
import json, sys, time, pathlib
event = json.load(sys.stdin)
line = {"ts": time.time(), "type": "human_prompt", "chars": len(event.get("prompt", ""))}
with pathlib.Path("ledger.ndjson").open("a") as f:
    f.write(json.dumps(line) + "\n")
```

Counting human prompts automatically is what makes the Human Touch Index honest: nobody has to remember to report their own interventions.

## 4. Experiment E3

Run the same five tasks with hooks disabled, then enabled. Compare retries, out-of-scope edits and human prompts. Write the counts in `docs/hook-impact.md` and say which hook you would not repeat.

## Checkpoint

- [ ] Hook files committed under `.kiro/hooks/` (never gitignored)
- [ ] Each hook shown firing at least once (screenshot or log)
- [ ] E3 logged
