---
description: Submit your understanding of the current step for evaluation — gates progression to the next step
allowed-tools: Read, Write, Edit, AskUserQuestion
---

Evaluate whether the student genuinely **understands** the current step — not whether output
happens to be correct. Understanding gates progression.

1. Read `.claude-learn/state.json` (current step + topic) and `.claude-learn/profile.json`.
   - **If `currentPhase` is `"mini_lesson"`**, there's nothing to check yet — the student
     hasn't been posed a problem for this step. Gently say so, ask if they're ready to move
     into the problem, and if yes, pose the step's Socratic question and set
     `currentPhase: "problem_solving"` (saved). Stop here; do not evaluate.
2. **Probe understanding.** Ask the student to explain their reasoning for this step in their
   own words: the *why*, and what would break if they did it differently. Ask one question at
   a time, warmly — not an interrogation. If they haven't said enough to judge, ask a single
   targeted follow-up before deciding (a beginner may need two short rounds instead of one
   dense one). Do not accept a pasted answer as proof — make them articulate the reasoning.
3. **Decide:**
   - **Pass** — they show real understanding:
     - Append `currentStep` to `completedSteps`, increment `currentStep`, set
       `awaitingCheck: false`, `currentPhase: "mini_lesson"`, reset `stopRedoCount: 0`, and
       save `state.json`.
     - If any concept is now solid, add it to `masteredConcepts` in `profile.json`.
     - Give specific, earned praise (name what they got right), then start the next step's
       **Mini Lesson** (per the cycle defined in `/learn`) — a CS50-style narrative
       explanation, length scaled to what the idea needs, aimed at that step's problem,
       teaching the new concept directly before posing any question; only move
       `currentPhase` to `"problem_solving"` once they signal they're ready. If that was the
       last step, congratulate them and summarize what they learned instead.
   - **Not yet** — gaps remain:
     - Do NOT advance. Name the specific gap.
     - Add the weak concept to `profile.json` `weakConcepts` (no duplicates) and to
       `reinforcementQueue` with a `priority` (1–10) reflecting how central it is.
     - Point them to `/hint` or `/explain <concept>` and tell them to `/check` again after.
4. Never give vague encouragement, but don't be cold either — name what they got right
   before naming the gap. Feedback must reference what they actually said.
