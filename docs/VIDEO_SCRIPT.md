# Demo video script (target 2:45, hard limit under 3:00)

Rules we follow (from the organisers' guidance): show it working in the first 10 to 15 seconds; start already logged in; no sign-up or setup on screen; cut all waiting; never type live (paste or cut to the result); one strong example per feature; jump cuts; record in short clips; on-screen text for key points; no music or trademarks without rights; team story stays in the written description.

**Show Kiro on screen**: at least one spec, one hook firing, and the steering folder.

## Shot list

| # | Time | On screen | Voice-over (short) | On-screen text |
|---|---|---|---|---|
| 1 | 0:00–0:12 | The morning briefing page: the guide ghost slides in with "While you slept: 7 shipped, 2 need you." Click "2 need you". | "I went to bed with one paragraph of intent. This is what was waiting this morning." | **Night Shift** · built with Kiro Crew + Kiro CLI |
| 2 | 0:12–0:25 | Split: last night's intent paragraph (left), merged PR list (right). | "Night Shift is a skeleton crew of AI agents that ships while your team sleeps." | *Intent in → verified code out* |
| 3 | 0:25–0:45 | Kiro IDE: the spec `requirements.md` with EARS criteria tagged `[PBT]`. Then the Spec Gate rejecting a vague requirement with the funny error. | "Nothing gets built from a vague wish. The Spec Gate sends unclear work back with a question." | **Kiro specs** · EARS + property tags |
| 4 | 0:45–1:05 | `.kiro/steering/` and `.kiro/agents/` folders, one role agent file. Cut to a hook JSON, then the hook firing in the session. | "Every agent shares the same org rules and only gets the tools its role needs. Hooks enforce them automatically." | **Steering · custom agents · hooks** |
| 5 | 1:05–1:30 | Time-lapse: Kiro Crew dashboard starting the Night Conductor; 4 terminals of headless `kiro-cli` workers in worktrees (sped up). | "At night, Kiro Crew runs headless Kiro CLI workers in parallel, each in its own worktree, on a credit budget." | **Kiro Crew → Kiro CLI headless** · sped up 20x |
| 6 | 1:30–1:50 | A property test failing with a shrunk counterexample, the agent fixing it, gate turns green. | "Property-based tests come straight from the requirements. Here one catches a bug that the example tests missed." | **PBT caught it** · [MEASURED] |
| 7 | 1:50–2:10 | Policy engine decision view: one change auto-merges (A1), one goes to the exception queue (A3, touches auth). | "A deterministic rulebook, not an agent, decides what merges. Auth changes always wait for a human." | *Risk can only go up* |
| 8 | 2:10–2:30 | Lazarus: legacy Perl page and the modern page side by side, parity score. Two-second Chimera clip: a shell-pipeline cell updating. | "Two apps from the same skeleton: a 2003 bulletin board resurrected with proof it behaves the same, and a spreadsheet stitched to the shell." | **Resurrection** + **Frankenstein** |
| 9 | 2:30–2:45 | Human Touch Index chart, first night vs last night. End card with repo and site URLs. | "Here is how often a human had to step in. It's open source, with build labs, so your team can run its own night shift." | [MEASURED numbers] · github.com/akashtalole/Kiroween2026 |

## Recording plan
- Record each row as its own clip; keep the best take.
- Pre-run everything; record results, not waiting. Replace long runs with a sped-up clip and label it.
- Use a 1080p window, large font (terminal 18pt+), dark theme, cursor highlight.
- Captions on for the whole video (also helps judges watching muted).
- No background music unless it is licensed for this use; silence is fine.
- Final check: duration under 3:00, public on YouTube, link in Devpost.
