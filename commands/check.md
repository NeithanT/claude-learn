---
description: Submit your understanding of the current step for evaluation — gates progression to the next step
allowed-tools: Read, Write, Edit, AskUserQuestion
---

Evaluate whether the student genuinely **understands** the current step — not whether output
happens to be correct. Understanding gates progression.

1. Read `.claude-learn/state.json` (current step + topic) and `.claude-learn/profile.json`.
2. **Probe understanding.** Ask the student to explain their reasoning for this step in their
   own words: the *why*, the trade-offs, and what would break if they did it differently. If
   they haven't said enough to judge, ask 1–2 targeted follow-up questions before deciding.
   Do not accept a pasted answer as proof — make them articulate the reasoning.
3. **Decide:**
   - **Pass** — they show real understanding:
     - Append `currentStep` to `completedSteps`, increment `currentStep`, set
       `awaitingCheck: false`, reset `stopRedoCount: 0`, and save `state.json`.
     - If any concept is now solid, add it to `masteredConcepts` in `profile.json`.
     - Give specific, earned praise (name what they got right), then present the next step as a
       question. If that was the last step, congratulate them and summarize what they learned.
   - **Not yet** — gaps remain:
     - Do NOT advance. Name the specific gap.
     - Add the weak concept to `profile.json` `weakConcepts` (no duplicates) and to
       `reinforcementQueue` with a `priority` (1–10) reflecting how central it is.
     - Point them to `/hint` or `/explain <concept>` and tell them to `/check` again after.
4. Never give vague encouragement. Feedback must reference what they actually said.
