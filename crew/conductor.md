# Conductor mode: the nightly goal

Use this when running the night by hand (first nights), before relying on the Night Conductor bot. Open a chat in this repo, turn on **conductor mode**, and paste:

> Goal for tonight: ship the top 4 spec-ready items in `backlog.json` within 400 credits.
> For each item, in parallel worker sessions: run `tools/run_task.sh <capability> builder`; then review the diff in a fresh `reviewer` session and a fresh `security` session; then run a `release` session to write `evidence/<capability>.md` and get the policy-check decision.
> Only a `merge` decision may land, and only on the integration branch. Park anything that fails three times, with what you tried. When done, run the morning-briefing skill.

Keep the conductor transcript link for `docs/kiro-log.md` (experiment E1, Crew column).
