---
description: Show your knowledge profile, active lesson status, and reinforcement queue
allowed-tools: Read
---

Render a concise progress report. Read `.claude-learn/profile.json` and
`.claude-learn/state.json` (either may be absent).

If no profile exists, tell the student to run `/learn` first.

Otherwise show:

1. **Knowledge profile** — each language/framework with its level (1–10). A simple bar like
   `python  ███████░░░ 7/10` is welcome.
2. **Active lesson** (if `state.json` has a topic) — topic, difficulty, and progress
   (`completedSteps` count of `steps` total), the current step description, and how many hints
   were used on it. If no lesson is active, say so and suggest `/learn <topic>`.
3. **Mastered concepts** — short list from `masteredConcepts`.
4. **Reinforcement queue** — `weakConcepts` / `reinforcementQueue` sorted by priority, with the
   top item highlighted and a nudge to run `/reinforce`.

Read-only: do not modify any state here.
