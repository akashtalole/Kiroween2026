# Kiro CLI automation

Everything Night Shift automates goes through the Kiro CLI in headless mode. This page is the operator's guide.

## The `nightshift` command

```bash
tools/nightshift/nightshift doctor                       # kiro-cli, agents, hooks, workflows, auth
tools/nightshift/nightshift run policy-engine            # one task end to end
tools/nightshift/nightshift night --workers 4 --limit 4  # the overnight run
tools/nightshift/nightshift review --base origin/main    # read-only review of a diff
tools/nightshift/nightshift triage build.log             # explain a failing build
tools/nightshift/nightshift workflow night-feature task="..." capability=x run_id=r1
```

### What `run` does

| Step | Mechanism |
|---|---|
| 1. Spec Gate | `spec_lint.py`. A spec that fails is **parked** with a ledger event, and Kiro is never called |
| 2. Isolation | `git worktree add -B ns/<capability>`, one per task, so parallel tasks never collide |
| 3. Build | `kiro-cli chat --v3 --no-interactive --output-format stream-json --agent builder --trust-tools=read,write,shell,grep,glob`. The prompt is sent on **stdin** |
| 4. Gate | `quick_gate.py --json-out evidence/<cap>.gate.json` (spec lint plus fast tests, machine-readable) |
| 5. Independent review | A **separate** headless session with the read-only `reviewer` agent. The builder's reasoning is never shared |
| 6. Decision | `policy_check.py`: a deterministic tier and decision (merge, queue_for_human or reject) |
| 7. Record | `evidence/<cap>.md`, plus `task_start` and `task_done` events in `ledger.ndjson` (credits, retries, tier) |

### Failure handling

| Situation | Behaviour |
|---|---|
| A `runError` record with `retryErrorType` THROTTLING (or a throttling `errorType`) | Retry with exponential backoff (2s, 4s, 8s), up to `--retries` |
| Exit code **3** (a required MCP server failed) or **4** (agent or mode not available) | `ConfigError`: stop immediately, no retries; `nightshift` exits 3 |
| Any other failure | Returned as-is; the gate and policy decide what happens next (usually `reject`) |
| Untrusted code (Lazarus legacy, Chimera shell cells) | Pass `--sandbox`; Kiro then refuses to start if the local command sandbox cannot activate |

### Least privilege

Each role gets a session-wide `--trust-tools` list (`ROLE_TRUST` in `ns.py`); the reviewer only gets `read,grep,glob`. The agent's own `permissions` rules then narrow that further: deny always wins. Headless V3 runs also load the workspace hooks, so the scope guard and secret scan apply to unattended work too. `--trust-all-tools` is never used.

### Budget

`night` reads `credits_per_night` and `parallel_workers` from `org/nightshift.yaml`. It stops scheduling new tasks at 80% of the budget (the cost governor's rule) and parks the rest. Credits are summed from the stream-json events. The field names vary by CLI version, so check the first real run's events and adjust `RunResult.credits` if needed.

## Workflow recipes (`.kiro/workflows/`)

| Recipe | Shape | Machine-checked stop |
|---|---|---|
| `night-feature` | requirements → design loop (max 3) → code loop (max 3) with **parallel** correctness and security reviews and an aggregator → validate | `design-review.json`, `code-review.json` verdict APPROVED; `gate.json` verdict PASS |
| `fix-until-green` | reproduce (read-only) → patch one cause per iteration (max 5) | `gate.json` verdict PASS |
| `lazarus-brownfield` | investigate the legacy app (read-only) → specify what it actually does → characterization tests | n/a |

Turn workflows on with `kiro-cli settings chat.enableWorkflows true`. Ask Kiro to `validate_workflow` a recipe before its first run. Headless runs wait for workflows to settle, for up to `KIRO_HEADLESS_WORKFLOW_TIMEOUT_SECS` (`nightshift workflow --timeout`). The recipes use our role agents. If Kiro says one is not workflow-capable, use the bundled agent named in the comment beside it.

## CI (`.github/workflows/`)

| Workflow | When | Needs |
|---|---|---|
| `ci.yml` | every push and PR | nothing: tests (including the orchestrator against a fake `kiro-cli`) and a secret scan |
| `kiro-review.yml` | every PR | `KIRO_API_KEY` repository secret; skipped without it. The verdict goes to the job summary |
| `kiro-nightly.yml` | manual (schedule commented out) | `KIRO_API_KEY`. Uploads `evidence/` and `ledger.ndjson` as an artifact; never pushes or merges |

## Testing the automation without spending credits

`tests/fakes/kiro-cli` imitates the CLI: success, a throttle followed by success, failure, a missing agent (exit 4) and an MCP failure (exit 3).

```bash
NS_KIRO_BIN=$PWD/tests/fakes/kiro-cli tools/nightshift/nightshift doctor
python3 -m pytest -q tests
```

## Verify on your machine before relying on it
- `kiro-cli --version` is 3.5 or later (for `runError` records and `--mode`).
- `nightshift doctor` lists all 8 agents, and Kiro loads them (`kiro-cli chat --agent reviewer` interactively).
- Run one real `nightshift run <capability> --in-place` and look at `evidence/` and `ledger.ndjson`.
