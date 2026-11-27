---
inclusion: always
---
# Tech

- **Orchestration and tools:** Python 3.11+, standard library first. Tests: `pytest` + `hypothesis`.
- **Chimera UI:** TypeScript, no framework unless a spec says so. Tests: `vitest` + `fast-check`.
- **Lazarus legacy app:** Perl 5, CGI, no CPAN dependencies (it must run on system Perl).
- **Agents:** Kiro CLI headless (`kiro-cli chat --v3 --no-interactive`) with scoped tool trust; Kiro Crew for bots and schedules.
- **Config:** `org/nightshift.yaml`. Secrets only from environment variables (`KIRO_API_KEY` etc.), never files in git.

**Rules**
- Prefer small, pure functions that are easy to property-test.
- No network calls in tests. No sleeping in tests.
- Pin dependency versions in lock or requirements files.
