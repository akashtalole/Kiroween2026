# Night Shift crew (Kiro Crew)

Kiro Crew bots are created in the Crew app, not from files: you open **Crewmates → New crewmate**, then the bot proposes its goal, milestones and check-ins as cards you accept. (Bots need **Settings → Developer → Feature Previews → Crewmates** on in Kiro Crew 0.10 or later.) This folder holds the **charters you paste in**, so every bot is reproducible and reviewable in git.

| File | What it is |
|---|---|
| `bots/*.md` | One charter per bot: name, goal, milestones, check-ins, allowed and forbidden actions, memory seeds |
| `conductor.md` | The nightly goal for **conductor mode** (one chat session coordinating worker sessions) |
| `schedules.md` | Natural-language schedules to add in the Schedule panel or by asking in chat |

## Set up (about 20 minutes)
1. Install and start Crew (`kirocrew setup`, `kirocrew doctor`, `kirocrew gateway`), sign in to `kiro-cli`.
2. Open this repository as the bot workspace.
3. For each file in `bots/`: **New crewmate** → paste the *Charter* section as the first message → accept the goal and milestone cards that match it → teach each *Memory seed* line as a separate message.
4. Add the schedules from `schedules.md`.
5. Run the conductor once by hand (`conductor.md`) before trusting the schedule.

## Evidence for the write-up
Screenshot each bot's goal card and one check-in, and keep the morning briefings in `docs/briefings/`. Note in `docs/kiro-log.md` anything Crew did differently from these charters; that difference is useful material for the "how did the surfaces differ" question.
