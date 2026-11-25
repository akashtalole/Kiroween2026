# Lab 06 · Two MCP servers: shared state and a legacy oracle

**Goal:** extend Kiro so agents on every surface share one view of the org, and so agents can interrogate real legacy behaviour instead of guessing. Experiments **E6** and **E8**.

> **Starting points, not yet run.** The shapes below follow the official Python MCP SDK as I know it. Check the current SDK version's API before relying on them.

## 1. `nightshift-mcp`: queue, ledger, policy

```python
# packages/nightshift-mcp/server.py
import json, pathlib
from mcp.server.fastmcp import FastMCP
from policy import Change, classify, decide  # the tested engine from Lab 05

mcp = FastMCP("nightshift")
LEDGER = pathlib.Path("ledger.ndjson")
QUEUE = pathlib.Path("backlog.json")

@mcp.tool()
def queue_next(n: int = 3) -> list:
    """Return the next n ranked, spec-approved tasks."""
    items = json.loads(QUEUE.read_text()) if QUEUE.exists() else []
    return [t for t in items if t.get("spec_ok")][:n]

@mcp.tool()
def policy_classify(paths: list[str], diff_lines: int, public_api_changed: bool = False,
                    deps_changed: bool = False, gates_passed: bool = True) -> dict:
    """Classify a change into a risk tier and decide merge, queue or reject."""
    c = Change(tuple(paths), diff_lines, public_api_changed, deps_changed, gates_passed)
    return {"tier": classify(c), "decision": decide(c)}

@mcp.tool()
def ledger_append(event: dict) -> str:
    """Append one event (task, human_touch, credits, retries) to the ledger."""
    with LEDGER.open("a") as f:
        f.write(json.dumps(event) + "\n")
    return "ok"

if __name__ == "__main__":
    mcp.run()
```

Register it for the project in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "nightshift": { "command": "python", "args": ["packages/nightshift-mcp/server.py"] }
  }
}
```

**Why it matters:** an IDE chat, a headless CLI worker and a Crew bot now read the same queue and write the same ledger. Without a shared tool, each surface would keep its own state.

## 2. `legacy-oracle-mcp`: ask the real legacy app

For Lazarus, run the legacy Perl CGI app in a sandbox and expose it as a tool, so agents writing specs can *query actual behaviour*:

```python
# apps/lazarus/oracle-mcp/server.py (sketch)
import subprocess, os
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("legacy-oracle")

@mcp.tool()
def request(method: str, path: str, body: str = "") -> dict:
    """Send one HTTP-like request to the legacy CGI app and return status, headers, body."""
    env = {**os.environ, "REQUEST_METHOD": method, "PATH_INFO": path, "CONTENT_LENGTH": str(len(body))}
    p = subprocess.run(["perl", "legacy/board.cgi"], input=body, text=True,
                       capture_output=True, env=env, timeout=5)
    return {"stdout": p.stdout, "stderr": p.stderr, "code": p.returncode}

if __name__ == "__main__":
    mcp.run()
```

Run it in a container with no network and a read-only code mount; the oracle executes only code we wrote ourselves.

## 3. Experiment E6

Write the Lazarus characterization specs twice: with and without the oracle. Count behaviours discovered, spec statements later contradicted by the oracle, and time taken. Log in `docs/mcp-impact.md`.

## 4. Package it as a Power (experiment E8)

Powers load on demand by keyword instead of loading every MCP tool up front. A power is a directory with a manifest, skills and optional MCP config:

```text
powers/night-shift/
├─ plugin.json        # manifest, activation keywords
├─ skills/spec-gate/SKILL.md
└─ mcp.json           # the nightshift server
```

Install it in IDE, CLI (V3) and Web (creating powers is IDE and CLI V3 only). Compare context size and task quality against always-on MCP, then trial 2 or 3 third-party powers from the registry and **keep only those that measurably help**. Record what you dropped and why in `docs/powers-trial.md`.

## Checkpoint

- [ ] `nightshift-mcp` callable from IDE, CLI and a Crew session
- [ ] Oracle used in at least one spec-writing session; E6 logged
- [ ] Power installed on three surfaces; E8 logged
