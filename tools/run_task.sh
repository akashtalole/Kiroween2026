#!/usr/bin/env bash
# Run one spec task headlessly in its own git worktree.
# Usage: tools/run_task.sh <capability> [agent]      e.g. tools/run_task.sh policy-engine builder
# Requires: kiro-cli (3.x), git. Auth: stored login or KIRO_API_KEY in the environment (never in files).
set -euo pipefail
CAP="$1"; AGENT="${2:-builder}"; ROOT="$(git rev-parse --show-toplevel)"
SPEC="$ROOT/.kiro/specs/$CAP"
[ -f "$SPEC/tasks.md" ] || { echo "No tasks.md for $CAP (run the analyst and architect first)"; exit 1; }
python3 "$ROOT/.kiro/skills/spec-gate/scripts/spec_lint.py" "$SPEC/requirements.md" || { echo "Spec Gate failed; parking $CAP"; exit 3; }
WT="$ROOT/../wt-$CAP"
git -C "$ROOT" worktree add -B "ns/$CAP" "$WT" HEAD >/dev/null 2>&1 || true
cd "$WT"
export NS_TASK="$CAP" NS_LEDGER="$ROOT/ledger.ndjson"
python3 tools/hooks/ledger.py task_start agent="$AGENT"
# Tool trust is scoped; the agent's own permissions narrow it further. Check `kiro-cli chat --help` for your version.
kiro-cli chat --v3 --no-interactive --agent "$AGENT" \
  "Implement the next unchecked task in .kiro/specs/$CAP/tasks.md. Follow your role exactly. Stop when tests are green or after 3 failed attempts." \
  || echo "kiro-cli exited non-zero; the gate below decides what happens next"
if python3 tools/hooks/quick_gate.py; then gates=yes; else gates=no; fi
python3 .kiro/skills/policy-check/scripts/policy_check.py --base HEAD~1 --gates-passed "$gates" --reviews 0 | tee "$ROOT/evidence/$CAP.policy.json"
python3 tools/hooks/ledger.py task_end gates="$gates"
