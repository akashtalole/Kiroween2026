#!/usr/bin/env python3
"""Governance linter for .kiro/agents: org-wide least-privilege rules as code. Exit 0 = compliant, 1 = violations."""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
READ_ONLY_ROLES = {"reviewer", "security"}
A3 = ["**/auth/**", "**/secrets/**", "infra/**", "**/migrations/**"]
DANGEROUS_SHELL = ["git push*", "rm -rf *", "sudo *"]


def load(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        import json
        return json.loads(text)
    parts = text.split("---\n")
    return yaml.safe_load(parts[1]) if text.startswith("---\n") and len(parts) > 2 else {}


def rules(cfg: dict, capability: str, effect: str) -> list[dict]:
    return [r for r in (cfg.get("permissions") or {}).get("rules", []) if r.get("capability") == capability and r.get("effect") == effect]


def lint_agent(name: str, cfg: dict) -> list[str]:
    v = []
    tools = cfg.get("tools") or []
    if not cfg.get("description"):
        v.append("missing description (other agents and humans pick agents by it)")
    if "*" in tools or "@builtin" in tools:
        v.append("uses a wildcard tool selector; list the tool categories it needs")
    if cfg.get("includeMcpJson") and "@mcp" not in tools and not cfg.get("mcpServers"):
        v.append("includeMcpJson is true but no MCP tools are selected; set it to false")
    writes = "write" in tools
    if name in READ_ONLY_ROLES:
        if writes:
            v.append("read-only role has the write tool")
        if not any("**" in r.get("match", []) for r in rules(cfg, "fs_write", "deny")):
            v.append("read-only role lacks an fs_write deny rule for **")
    if writes:
        allow = rules(cfg, "fs_write", "allow")
        if not allow:
            v.append("can write but has no fs_write allow rule scoping where")
        if any("**" in r.get("match", []) and not r.get("exclude") for r in allow):
            v.append("fs_write allows ** without exclusions")
        denied = [m for r in rules(cfg, "fs_write", "deny") for m in r.get("match", [])]
        allowed = [m for r in allow for m in r.get("match", [])]
        broad = any(a.startswith(("apps/", "tools/", "src/")) and not a.endswith(".md") for a in allowed)
        if broad and not all(g in denied for g in A3):
            v.append("writes code but does not deny every tier A3 path " + str(A3))
    if "shell" in tools:
        if not rules(cfg, "shell", "allow"):
            v.append("has shell but no shell allow rule listing commands")
        denied_sh = [m for r in rules(cfg, "shell", "deny") for m in r.get("match", [])]
        allowed_sh = [m for r in rules(cfg, "shell", "allow") for m in r.get("match", [])]
        if any(a in ("*", "**") for a in allowed_sh):
            v.append("shell allows every command")
        if name == "builder" and not all(d in denied_sh for d in DANGEROUS_SHELL):
            v.append(f"builder must deny {DANGEROUS_SHELL}")
    return v


def main(argv: list[str]) -> int:
    folder = pathlib.Path(argv[1]) if len(argv) > 1 else ROOT / ".kiro" / "agents"
    bad = 0
    for f in sorted(list(folder.glob("*.md")) + list(folder.glob("*.json"))):
        cfg = load(f)
        name = cfg.get("name") or f.stem
        problems = lint_agent(name, cfg)
        bad += len(problems)
        print(f"{'OK  ' if not problems else 'FAIL'} {name}")
        for p in problems:
            print(f"       - {p}")
    print(f"\nAgent governance: {'compliant' if not bad else f'{bad} violation(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
