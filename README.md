# 🌙 Night Shift

**A skeleton crew of AI agents that ships while your team sleeps.**

You write one paragraph of intent before you log off. Overnight, Kiro agents turn it into a spec, build it in parallel, test it with property-based tests, and a rulebook decides what is safe to merge. In the morning a ghost hands you one page: what shipped, what needs you, and what it cost.

| | |
|---|---|
| **What** | An open-source "engineering org in a box" built on Kiro CLI + Kiro Crew: specs, steering, hooks, role agents, MCP and a deterministic merge policy |
| **Who** | Small teams and solo maintainers who have more backlog than hours, and enterprises piloting AI-first delivery |
| **Why** | Agents are fast but need babysitting. Night Shift makes intent explicit, verifies correctness automatically, and only wakes a human for real decisions, then **measures** how often that was |

> **Status (Nov 26, 2026):** design and site are done; the build is in progress during the Kiroween 2026 submission window. Numbers below are filled in only once measured.

## Built with Kiro

| Kiro feature | How Night Shift uses it |
|---|---|
| **Kiro Crew** | Bots (intake, pipeline health, docs sync, cost governor, morning briefing), conductor mode, nightly schedules |
| **Kiro CLI** | Headless workers (`--no-interactive`) in parallel git worktrees |
| **Kiro IDE / Web** | Specs and steering authoring, spec property tests (IDE); scheduled PRs (Web) |
| **Specs** | EARS requirements tagged `[PBT]` / `[EX]`, a Spec Gate that blocks vague work |
| **Steering** | Org golden rules plus per-role "must not" files |
| **Hooks** | Spec gate, scope guard, test on save, touch logger, gate on stop |
| **Custom agents** | Eight least-privilege roles: analyst, architect, builder, tester, reviewer, security, scribe, release |
| **MCP** | `nightshift-mcp` (shared queue, ledger, policy) and `legacy-oracle-mcp` (ask the real legacy app) |
| **Property-based testing** | Merge policy can only get stricter; parity between legacy and modern apps |
| **Powers** | A `night-shift` power packaging the Spec Gate, plus trialled third-party powers |

Everything Kiro produced lives in [`/.kiro`](.kiro) at the repo root.

## One skeleton, two apps (Skeleton Crew)

- **`apps/lazarus`** (Resurrection): a 2003-style Perl CGI bulletin board, specified from its real behaviour, rewritten by agents, proven equivalent with differential tests.
- **`apps/chimera`** (Frankenstein): a spreadsheet whose cells are formulas, shell pipelines or HTTP calls, built from one paragraph of intent.

## Try it

- 🌐 **Site, ideas and build labs:** https://akashtalole.github.io/Kiroween2026/ (after Pages is enabled)
- 🧪 **Tested example:** `examples/policy-engine` (`pip install hypothesis pytest && python -m pytest -q`)
- 📐 **Design:** [`docs/NIGHT_SHIFT.md`](docs/NIGHT_SHIFT.md) · **Kiro feature plan:** [`docs/KIRO_FEATURE_PLAN.md`](docs/KIRO_FEATURE_PLAN.md)

## Secrets

Never commit keys. Headless runs read `KIRO_API_KEY` from the environment; `.env` files are gitignored. Run `bash tools/presubmit-check.sh` before pushing.

## License

[MIT](LICENSE) (see the LICENSE file for the exact terms).
