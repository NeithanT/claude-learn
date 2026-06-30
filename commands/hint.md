---
description: Get the next hint for the current lesson step — escalates directional → structural → near-explicit
allowed-tools: Read, Write, Edit
---

Deliver the next hint on the 3-level ladder for the **current** lesson step.

1. Read `.claude-learn/state.json`. Find `currentStep` and the count in
   `hintsUsed[currentStep]` (default 0).
2. The hint level is `hintsUsed[currentStep] + 1`:
   - **Level 1 — directional**: point at the right area / concept / question to ask. No structure.
   - **Level 2 — structural**: outline the approach or the shape of the solution (steps,
     data structures, the key decision) — still no working code.
   - **Level 3 — near-explicit / partial**: the most specific help short of the full answer —
     e.g. pseudocode or a 1–3 line fragment of the hardest part, with the rest left to them.
   - If already at 3, give the level-3 hint again, reframed, and gently point them to `/check`
     or `/explain <concept>`. Never produce the complete solution.
3. Calibrate wording to the student's profile level (analogies for low levels; precise terms
   for high levels).
4. Increment `hintsUsed[currentStep]` in `state.json` and save it (this path is write-allowed).
5. Give exactly one hint at the computed level. End with a question that nudges their next move.
