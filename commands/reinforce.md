---
description: Run a targeted Socratic session on your highest-priority weak concept
allowed-tools: Read, Write, Edit, AskUserQuestion
---

Run a focused reinforcement session on the student's weakest concept.

1. Read `.claude-learn/profile.json`. Pick the highest-`priority` item in `reinforcementQueue`
   (fall back to the first `weakConcepts` entry). If both are empty, tell the student they have
   no weak concepts queued and suggest `/learn <topic>` or `/progress`.
2. Run a short Socratic drill on that concept: one warm, concrete question that surfaces the
   misunderstanding (use a fresh, friendly analogy, not a re-run of the original failure), then
   guide with the `/hint` ladder as needed. Do NOT write the solution — make them work it.
   Use a *fresh* example, not the one they previously struggled with.
3. Judge their responses the way `/check` does — probe the reasoning, don't accept pasted output.
4. **Update `profile.json`:**
   - If they now demonstrate mastery: remove the concept from `weakConcepts` and
     `reinforcementQueue`, and add it to `masteredConcepts`. Celebrate specifically.
   - If still shaky: keep it queued but adjust its `priority`, and note what to revisit.
5. Keep it tight — one concept per session.
