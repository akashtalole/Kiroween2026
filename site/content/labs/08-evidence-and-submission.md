# Lab 08 · Evidence, write-up and submission

**Goal:** turn the log into the write-up, and ship a submission that cannot be disqualified on a technicality.

## 1. Fill the write-up from the log

Open `docs/WRITEUP.md`. Every `[FILL]` must be replaced by a number or sentence with a matching entry in `docs/kiro-log.md`. Delete anything you cannot back up. Results that showed no difference are welcome; they make the rest more believable.

## 2. Compute the Human Touch Index

From `ledger.ndjson`:

- zero-touch rate (tasks merged with no human event)
- touches per task and human seconds per merged task
- first-pass gate rate and retries per task
- credits per merged task
- escapes (defects found after merge; seed a canary bug to test the gates)

Report the first night and the last night side by side.

## 3. Repository requirements (from the official rules)

- [ ] Public **GitHub** repository (not GitLab or Bitbucket) with all source, assets and instructions
- [ ] **Open-source license** detectable at the top of the repo page (the *About* box)
- [ ] **`/.kiro` directory at the root**, and not in `.gitignore`, showing specs, hooks and steering
- [ ] **Skeleton Crew:** two separate app folders (`apps/lazarus`, `apps/chimera`)
- [ ] Built during the submission period (Oct 30 to Dec 4, 2026); nothing reused from earlier projects
- [ ] Working app URL or run instructions; credentials for judges in the form's private field
- [ ] Text description of features and functionality

## 4. Video (under three minutes, public on YouTube)

| Time | Beat |
|---|---|
| 0:00 | The problem and the thesis |
| 0:20 | The morning briefing after a real night |
| 0:50 | An intent paragraph through the Spec Gate |
| 1:20 | Parallel workers; a gate fails, retries, passes |
| 1:50 | Policy engine: one change auto-merges, one goes to the queue |
| 2:20 | Lazarus parity result and Chimera running |
| 2:45 | Human Touch Index, and "what a human still had to do" |

No third-party trademarks or copyrighted music. Show it working on the device it was built for.

## 5. Bonus prizes

| Bonus | What you need |
|---|---|
| Best Kiro Crew App | A separate public repo for the Crew app, **newly created in the submission period**, on the same GitHub account |
| Bonus Blog Prize | A public post on a third-party platform during the period, mentioning it is written for the Kiroween 2026 hackathon |
| Social Blitz | A public post starting with `#KiroweenHackathon26`, with your real favourite thing about Kiro |
| Best Demo | Free with an excellent video, if you are in the top 10% overall |
| Student / Startup / Ghost of Kiroween Past | Only if every condition is true for you |

## 6. Final checks

```bash
git clone <your-repo> fresh && cd fresh
ls -a | grep .kiro          # must exist
grep -n kiro .gitignore     # must print nothing
```

- [ ] Fresh clone runs from the README in under ten minutes
- [ ] No secrets in history
- [ ] Credit form submitted before Dec 1, 12:00 pm PT
- [ ] **Submit on Dec 3.** Dec 4 is buffer only (deadline 2:00 pm PT)
