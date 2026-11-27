#!/usr/bin/env python3
"""nightshift: drive Kiro CLI headlessly for Night Shift.

Subcommands
  doctor                     check kiro-cli, agents, hooks, workflows and auth hints
  run <capability>           one spec task: worktree -> builder -> gate -> fresh reviewer -> policy -> evidence
  night                      the overnight run: top spec-ready backlog items in parallel, under a credit budget
  review [--base REF]        headless read-only review of a diff; non-zero exit on request-changes
  triage <logfile>           explain a failing build from its log (log piped on stdin, read-only tools)
  workflow <name> [k=v ...]  run a saved .kiro/workflows recipe headlessly and wait for it to settle
  plan <capability>          show dependency-aware waves of unfinished tasks (parallel-safe, no file clashes)
  questions [--accept-defaults]  list open spec questions; optionally accept every recommended default
  cloud <capability> --repo owner/name  run the next task in a Kiro cloud session that opens a PR (never merges)

Everything Kiro does goes through `kiro-cli chat --v3 --no-interactive --output-format stream-json`.
Exit codes from kiro-cli: 0 ok, 1 failure, 3 required MCP server failed, 4 agent or mode not available.
Throttled runs (runError with retryErrorType THROTTLING) are retried with exponential backoff.
Set NS_KIRO_BIN to point at another binary (the tests use a fake). Never put keys in files: use KIRO_API_KEY.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import dataclasses
import json
import os
import pathlib
import re
import subprocess
import sys
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "frontier"))
import task_dag  # noqa: E402
KIRO = os.environ.get("NS_KIRO_BIN", "kiro-cli")
LEDGER = pathlib.Path(os.environ.get("NS_LEDGER", ROOT / "ledger.ndjson"))
EVIDENCE = ROOT / "evidence"

# Session-wide tool trust per role. The agent's own permission rules narrow this further (deny always wins).
ROLE_TRUST = {
    "analyst": "read,write,grep,glob",
    "architect": "read,write,grep,glob",
    "builder": "read,write,shell,grep,glob",
    "tester": "read,write,shell,grep,glob",
    "reviewer": "read,grep,glob",
    "security": "read,shell,grep,glob",
    "scribe": "read,write,grep,glob",
    "release": "read,write,shell,grep,glob",
}
RETRYABLE = {"THROTTLING", "TRANSIENT", "SERVICE_UNAVAILABLE"}
_ledger_lock = threading.Lock()


class ConfigError(RuntimeError):
    """kiro-cli is misconfigured (exit 3 or 4): retrying will not help."""


@dataclasses.dataclass
class RunResult:
    exit_code: int
    events: list
    text: str
    error: dict | None
    attempts: int
    seconds: float

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and self.error is None

    @property
    def credits(self) -> float:
        """Sum any credit/cost figures present in the event stream (field names vary by version)."""
        total = 0.0
        for e in self.events:
            for k, v in _walk_items(e):
                if k in ("credits", "creditsUsed", "credit_usage", "cost") and isinstance(v, (int, float)):
                    total += float(v)
        return total


def _walk_items(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from _walk_items(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk_items(v)


def ledger(event: dict) -> None:
    event.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%S"))
    event.setdefault("night", time.strftime("%Y-%m-%d", time.localtime(time.time() - 12 * 3600)))
    with _ledger_lock, LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def build_cmd(agent: str | None, *, trust: str | None = None, sandbox: bool = False, require_mcp: bool = False,
              model: str | None = None, effort: str | None = None, resume_id: str | None = None,
              cloud: bool = False, repo: str | None = None) -> list[str]:
    cmd = [KIRO, "chat", "--v3", "--no-interactive", "--output-format", "stream-json"]
    if agent:
        cmd += ["--agent", agent]
    trust = trust or (ROLE_TRUST.get(agent or "", "read,grep,glob"))
    cmd.append(f"--trust-tools={trust}")
    if sandbox:
        cmd.append("--sandbox")
    if require_mcp:
        cmd.append("--require-mcp-startup")
    if model:
        cmd += ["--model", model]
    if effort:
        cmd += ["--effort", effort]
    if resume_id:
        cmd += ["--resume-id", resume_id]
    if cloud:
        cmd.append("--cloud")
        if repo:
            cmd += ["--repo", repo]
    return cmd


def parse_stream(stdout: str) -> tuple[list, str, dict | None]:
    events, texts, error = [], [], None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            texts.append(line)
            continue
        events.append(ev)
        if ev.get("type") == "runError":
            error = ev.get("data", {}) or {}
        for k, v in _walk_items(ev):
            if k in ("text", "content", "message") and isinstance(v, str):
                texts.append(v)
    return events, "\n".join(texts), error


def run_kiro(prompt: str, agent: str | None, *, cwd: pathlib.Path = ROOT, retries: int = 3,
             sleep=time.sleep, env: dict | None = None, **flags) -> RunResult:
    """Run one headless Kiro session; prompt goes on stdin (no quoting or argv-length problems)."""
    cmd = build_cmd(agent, **flags)
    started, attempt = time.time(), 0
    while True:
        attempt += 1
        p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=cwd,
                           env={**os.environ, **(env or {})})
        events, text, error = parse_stream(p.stdout)
        if p.returncode in (3, 4):
            raise ConfigError(f"kiro-cli exit {p.returncode}: {(p.stderr or text).strip()[:400]}")
        retryable = bool(error) and (str(error.get("retryErrorType", "")).upper() in RETRYABLE
                                     or "throttl" in str(error.get("errorType", "")).lower())
        if retryable and attempt <= retries:
            wait = 2 ** attempt
            print(f"  throttled; retrying in {wait}s (attempt {attempt}/{retries})", file=sys.stderr)
            sleep(wait)
            continue
        return RunResult(p.returncode, events, text, error, attempt, round(time.time() - started, 1))


# ----------------------------------------------------------------------------- helpers
def sh(cmd: list[str], cwd: pathlib.Path = ROOT, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check, stdin=subprocess.DEVNULL)


def spec_ready(cap: str, root: pathlib.Path = ROOT) -> bool:
    req = root / ".kiro" / "specs" / cap / "requirements.md"
    tasks = root / ".kiro" / "specs" / cap / "tasks.md"
    if not (req.exists() and tasks.exists()):
        return False
    return sh([sys.executable, ".kiro/skills/spec-gate/scripts/spec_lint.py", str(req)], cwd=root).returncode == 0


def make_worktree(cap: str) -> pathlib.Path:
    wt = ROOT.parent / f"wt-{cap}"
    if not wt.exists():
        sh(["git", "worktree", "add", "-B", f"ns/{cap}", str(wt), "HEAD"], check=True)
    return wt


def verdict_of(text: str) -> str:
    m = re.search(r"verdict\W{0,6}(approve|request-changes)", text, re.I)
    return m.group(1).lower() if m else "unknown"


def policy(cwd: pathlib.Path, gates_passed: bool, reviews: int) -> dict:
    p = sh([sys.executable, ".kiro/skills/policy-check/scripts/policy_check.py", "--base", "HEAD~1",
            "--gates-passed", "yes" if gates_passed else "no", "--reviews", str(reviews)], cwd=cwd)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"decision": "queue_for_human", "tier": "unknown", "signals": ["policy check could not run"],
                "stderr": p.stderr[-300:]}


# ----------------------------------------------------------------------------- commands
def cmd_doctor(a) -> int:
    ok = True
    v = sh([KIRO, "--version"]) if _which(KIRO) else None
    print(f"kiro-cli: {v.stdout.strip() if v and v.returncode == 0 else 'NOT FOUND (curl -fsSL https://cli.kiro.dev/install | bash)'}")
    ok &= bool(v and v.returncode == 0)
    agents = sorted(p.stem for p in (ROOT / ".kiro/agents").glob("*.md"))
    missing = [r for r in ROLE_TRUST if r not in agents]
    print(f"agents: {', '.join(agents) or 'none'}" + (f"  MISSING: {missing}" if missing else ""))
    ok &= not missing
    for f in sorted((ROOT / ".kiro/hooks").glob("*.json")):
        try:
            h = json.loads(f.read_text())["hooks"][0]
            print(f"hook: {f.stem:16} trigger={h['trigger']:18} enabled={h.get('enabled', True)}")
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"hook: {f.name} INVALID ({e})"); ok = False
    wfs = sorted(p.name for p in (ROOT / ".kiro/workflows").glob("*.workflow.*"))
    print(f"workflows: {', '.join(wfs) or 'none'} (enable with: kiro-cli settings chat.enableWorkflows true)")
    print("auth: " + ("KIRO_API_KEY is set" if os.environ.get("KIRO_API_KEY") else "using stored login (kiro-cli login) if present"))
    return 0 if ok else 1


def _which(name: str) -> bool:
    return any((pathlib.Path(d) / name).exists() for d in os.environ.get("PATH", "").split(os.pathsep)) or os.path.exists(name)


def next_task(cap: str, root: pathlib.Path = ROOT) -> int | None:
    """Lowest-numbered unfinished task whose dependencies are done (see tools/frontier/task_dag.py)."""
    f = root / ".kiro" / "specs" / cap / "tasks.md"
    ready = task_dag.next_ready(task_dag.parse(f.read_text(encoding="utf-8"))) if f.exists() else []
    return ready[0] if ready else None


def review_panel(prompt: str, models: list | None, *, cwd: pathlib.Path = ROOT, retries: int = 3, sleep=time.sleep,
                 env: dict | None = None) -> dict:
    """Independent reviews in parallel, one fresh read-only session per model. Approve only if every reviewer approves.

    Frontier teams use reviewers on different models so their findings are independent in more than name.
    """
    models = models or [None]
    with cf.ThreadPoolExecutor(max_workers=len(models)) as pool:
        runs = list(pool.map(lambda m: run_kiro(prompt, "reviewer", cwd=cwd, retries=retries, sleep=sleep, env=env, model=m), models))
    verdicts = [verdict_of(r.text) for r in runs]
    return {"verdict": "approve" if all(v == "approve" for v in verdicts) else "request-changes",
            "verdicts": dict(zip([m or "default" for m in models], verdicts)),
            "text": "\n\n---\n\n".join(f"### Reviewer ({m or 'default'})\n{r.text}" for m, r in zip(models, runs)),
            "credits": sum(r.credits for r in runs), "attempts": sum(r.attempts for r in runs),
            "seconds": max(r.seconds for r in runs)}


def run_capability(cap: str, *, use_worktree: bool = True, sandbox: bool = False, retries: int = 3,
                   sleep=time.sleep, review_models: list | None = None) -> dict:
    """One task, end to end. Returns a summary dict (also written to the ledger and evidence/)."""
    if not spec_ready(cap):
        ledger({"type": "parked", "task": cap, "reason": "spec not ready (Spec Gate)"})
        return {"task": cap, "status": "parked", "reason": "spec not ready"}
    task_no = next_task(cap)
    if task_no is None:
        ledger({"type": "nothing_to_do", "task": cap})
        return {"task": cap, "status": "done", "reason": "no unfinished task with satisfied dependencies"}
    cwd = make_worktree(cap) if use_worktree else ROOT
    env = {"NS_TASK": cap, "NS_LEDGER": str(LEDGER)}
    ledger({"type": "task_start", "task": cap, "task_no": task_no})
    build = run_kiro(f"Implement task {task_no} (and only task {task_no}) in .kiro/specs/{cap}/tasks.md. Follow your role exactly. "
                     "Stop when the tests are green or after 3 failed attempts, and say which.",
                     "builder", cwd=cwd, retries=retries, sleep=sleep, sandbox=sandbox, env=env)
    gate_file = EVIDENCE / f"{cap}.gate.json"
    EVIDENCE.mkdir(exist_ok=True)
    gates_passed = sh([sys.executable, "tools/hooks/quick_gate.py", "--json-out", str(gate_file)], cwd=cwd).returncode == 0
    diff = sh(["git", "diff", "HEAD~1"], cwd=cwd).stdout[-60000:]
    review = review_panel("You are reviewing a change you did not write. Requirements: "
                          f".kiro/specs/{cap}/requirements.md. Start your answer with 'Verdict: approve' or "
                          f"'Verdict: request-changes'.\n\n```diff\n{diff}\n```", review_models, cwd=cwd,
                          retries=retries, sleep=sleep, env=env)
    verdict = review["verdict"]
    decision = policy(cwd, gates_passed and build.ok, 2 if verdict == "approve" else 0)
    credits = build.credits + review["credits"]
    summary = {"task": cap, "task_no": task_no, "reviewers": review["verdicts"], "status": decision.get("decision"), "tier": decision.get("tier"),
               "build_exit": build.exit_code, "build_error": build.error, "gates_passed": gates_passed,
               "review": verdict, "signals": decision.get("signals", []), "credits": credits,
               "attempts": build.attempts + review["attempts"], "seconds": build.seconds + review["seconds"]}
    (EVIDENCE / f"{cap}.md").write_text(_evidence_md(summary, review["text"]), encoding="utf-8")
    ledger({"type": "task_done", "task": cap, "merged": decision.get("decision") == "merge",
            "retries": max(0, build.attempts - 1), "credits": credits, "tier": decision.get("tier")})
    return summary


def _evidence_md(s: dict, review_text: str) -> str:
    return (f"# Evidence: {s['task']}\n\n## Policy decision\n`{s['status']}` (tier {s['tier']}); signals: "
            f"{', '.join(s['signals']) or 'none'}\n\n## Gates\nquick gate: {'pass' if s['gates_passed'] else 'fail'} "
            f"(details in `{s['task']}.gate.json`); builder exit {s['build_exit']}\n\n## Review\nverdict: {s['review']}\n\n"
            f"<details><summary>Reviewer output</summary>\n\n{review_text[:6000]}\n\n</details>\n\n## Cost\n"
            f"credits: {s['credits']} · attempts: {s['attempts']} · seconds: {s['seconds']}\n")


def cmd_run(a) -> int:
    s = run_capability(a.capability, use_worktree=not a.in_place, sandbox=a.sandbox, retries=a.retries,
                       review_models=_models(a))
    print(json.dumps(s, indent=2, default=str))
    return 0 if s["status"] in ("merge", "queue_for_human") else 1


def load_budget() -> tuple[float, float, int]:
    text = (ROOT / "org/nightshift.yaml").read_text(encoding="utf-8")
    get = lambda k, d: float(m.group(1)) if (m := re.search(rf"{k}:\s*([\d.]+)", text)) else d  # noqa: E731
    return get("credits_per_night", 400.0), get("per_task_cap", 60.0), int(get("parallel_workers", 4))


def cmd_night(a) -> int:
    budget, _cap, workers = load_budget()
    workers = a.workers or workers
    items = json.loads((ROOT / "backlog.json").read_text(encoding="utf-8") or "[]")
    queue = [i["capability"] for i in sorted(items, key=lambda i: i.get("rank", 999))]
    ready = [c for c in queue if spec_ready(c)]
    for c in set(queue) - set(ready):
        ledger({"type": "parked", "task": c, "reason": "spec not ready (Spec Gate)"})
    print(f"Night run: {len(ready)} ready, {len(queue) - len(ready)} parked, {workers} workers, budget {budget:.0f} credits")
    spent, results = 0.0, []
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        pending = {}
        for cap in ready[: a.limit or len(ready)]:
            if spent >= budget * 0.8:  # the cost governor's 80% rule
                ledger({"type": "parked", "task": cap, "reason": "night budget at 80%"})
                continue
            pending[pool.submit(run_capability, cap, use_worktree=not a.in_place, sandbox=a.sandbox,
                                 review_models=_models(a))] = cap
        for fut in cf.as_completed(pending):
            try:
                r = fut.result()
            except ConfigError as e:
                r = {"task": pending[fut], "status": "config_error", "error": str(e)}
            spent += float(r.get("credits") or 0)
            results.append(r)
            print(f"  {r['task']:24} {r['status']:16} tier={r.get('tier', '-')}")
    print(json.dumps({"spent_credits": spent, "results": results}, indent=2, default=str)[:4000])
    return 0


def cmd_review(a) -> int:
    diff = sh(["git", "diff", a.base]).stdout
    if not diff.strip():
        print("Nothing to review."); return 0
    r = review_panel("Review this diff against .kiro/steering. Start with 'Verdict: approve' or 'Verdict: request-changes', "
                     f"then list findings as file:line, problem, fix.\n\n```diff\n{diff[-60000:]}\n```", _models(a),
                     retries=a.retries)
    EVIDENCE.mkdir(exist_ok=True)
    head = sh(["git", "rev-parse", "--short", "HEAD"]).stdout.strip() or "worktree"
    out = EVIDENCE / f"review-{head}.md"
    out.write_text(r["text"], encoding="utf-8")
    v = r["verdict"]
    print(f"Review verdict: {v} {r['verdicts']} (full text in {out.relative_to(ROOT)})")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"## Kiro review: {v}\n\n{r['text'][:20000]}\n")
    return 0 if v == "approve" else 2


def cmd_triage(a) -> int:
    log = pathlib.Path(a.logfile).read_text(encoding="utf-8", errors="ignore")[-40000:]
    r = run_kiro("Explain this build failure: the first real error, the likely cause (cite files), and the smallest fix. "
                 "Do not change any files.\n\n" + log, "reviewer", retries=a.retries)
    print(r.text or f"(no text; exit {r.exit_code}, error {r.error})")
    return 0 if r.ok else 1


def cmd_workflow(a) -> int:
    inputs = dict(kv.split("=", 1) for kv in a.inputs)
    prompt = (f"Run the saved workflow `{a.name}` with these inputs: {json.dumps(inputs)}. Do not change the recipe. "
              "When it settles, report its outcome and the paths of its artifacts.")
    env = {"KIRO_HEADLESS_WORKFLOW_TIMEOUT_SECS": str(a.timeout)}
    r = run_kiro(prompt, None, trust=a.trust, retries=a.retries, env=env)
    outcome = next((o for o in ("completed", "failed", "aborted", "paused") if re.search(rf"\b{o}\b", r.text)), "unknown")
    ledger({"type": "workflow", "name": a.name, "outcome": outcome, "credits": r.credits, "seconds": r.seconds})
    print(f"Workflow {a.name}: {outcome}")
    return 0 if outcome == "completed" else 1


def _models(a) -> list | None:
    return [m.strip() for m in a.review_models.split(",") if m.strip()] if getattr(a, "review_models", None) else None


def cmd_plan(a) -> int:
    f = ROOT / ".kiro" / "specs" / a.capability / "tasks.md"
    if not f.exists():
        print(f"No tasks.md for {a.capability}"); return 1
    return task_dag.main(["task_dag", str(f)])


QUESTION = re.compile(r"^(\s*[-*]\s+)(.*?recommended default:\s*)(.+)$", re.I)


def cmd_questions(a) -> int:
    """The question queue: agents park ambiguity with a recommended default instead of guessing."""
    found = 0
    for req in sorted((ROOT / ".kiro" / "specs").glob("*/requirements.md")):
        lines, changed, in_q = req.read_text(encoding="utf-8").splitlines(), False, False
        for i, line in enumerate(lines):
            if re.match(r"^#{2,3}\s+Open questions", line, re.I):
                in_q = True; continue
            if in_q and line.startswith("#"):
                in_q = False
            m = QUESTION.match(line) if in_q else None
            if not m or "decision:" in line.lower():
                continue
            found += 1
            print(f"{req.parent.name}: {m.group(2).split('Recommended')[0].strip()}  -> default: {m.group(3).strip()}")
            if a.accept_defaults:
                lines[i] = f"{line} Decision: default accepted {time.strftime('%Y-%m-%d')}."
                changed = True
                ledger({"type": "human_approval", "task": req.parent.name, "seconds": 0, "what": "accepted default"})
        if changed:
            req.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{found} open question(s)" + (" accepted with their defaults" if a.accept_defaults and found else ""))
    return 0


def cmd_cloud(a) -> int:
    """Kiro Web cloud session: works while your laptop sleeps, opens a PR, never merges."""
    task_no = next_task(a.capability)
    if task_no is None or not spec_ready(a.capability):
        print("Nothing ready to run (spec not ready or no unblocked task)."); return 1
    r = run_kiro(f"In repository {a.repo}, implement task {task_no} of .kiro/specs/{a.capability}/tasks.md on a new "
                 f"branch ns/{a.capability}-{task_no}, run the tests, and open a pull request whose description is the "
                 "evidence pack from .kiro/skills/evidence-pack. Do not merge.", None, cloud=True, repo=a.repo,
                 trust=a.trust, retries=a.retries)
    ledger({"type": "cloud_task", "task": a.capability, "task_no": task_no, "exit": r.exit_code, "credits": r.credits})
    print(r.text[-3000:] or f"exit {r.exit_code} {r.error}")
    return 0 if r.ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nightshift", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    r = sub.add_parser("run"); r.add_argument("capability")
    n = sub.add_parser("night"); n.add_argument("--workers", type=int); n.add_argument("--limit", type=int)
    for p in (r, n):
        p.add_argument("--review-models", help="comma-separated model IDs for independent parallel reviewers")
        p.add_argument("--in-place", action="store_true", help="no worktree (tests, quick experiments)")
        p.add_argument("--sandbox", action="store_true", help="require the local command sandbox")
        p.add_argument("--retries", type=int, default=3)
    r.set_defaults(fn=cmd_run); n.set_defaults(fn=cmd_night)
    v = sub.add_parser("review"); v.add_argument("--base", default="origin/main"); v.add_argument("--retries", type=int, default=3)
    v.add_argument("--review-models", help="comma-separated model IDs; approve only if all approve")
    pl = sub.add_parser("plan"); pl.add_argument("capability"); pl.set_defaults(fn=cmd_plan)
    q = sub.add_parser("questions"); q.add_argument("--accept-defaults", action="store_true"); q.set_defaults(fn=cmd_questions)
    c = sub.add_parser("cloud"); c.add_argument("capability"); c.add_argument("--repo", required=True)
    c.add_argument("--trust", default="read,write,shell,grep,glob"); c.add_argument("--retries", type=int, default=2)
    c.set_defaults(fn=cmd_cloud)
    v.set_defaults(fn=cmd_review)
    t = sub.add_parser("triage"); t.add_argument("logfile"); t.add_argument("--retries", type=int, default=3)
    t.set_defaults(fn=cmd_triage)
    w = sub.add_parser("workflow"); w.add_argument("name"); w.add_argument("inputs", nargs="*")
    w.add_argument("--timeout", type=int, default=7200); w.add_argument("--trust", default="read,write,shell,grep,glob")
    w.add_argument("--retries", type=int, default=2); w.set_defaults(fn=cmd_workflow)
    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except ConfigError as e:
        print(f"Configuration problem, not retrying: {e}", file=sys.stderr)
        return 3
    except FileNotFoundError as e:
        print(f"Missing file or binary: {e}. Run `nightshift doctor`.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
