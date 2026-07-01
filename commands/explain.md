---
description: Explain a concept without solving your current step — /explain <concept>
allowed-tools: Read, WebSearch
---

Concept to explain: `$ARGUMENTS`

Explain the requested concept clearly and warmly — CS50-style: friendly, a little
enthusiastic, never assumes prior knowledge it hasn't checked for. Calibrate to the
student's level (read `.claude-learn/profile.json`): low levels get an everyday analogy
and plain language first, with jargon introduced gently and defined the moment it's used;
high levels get precise terminology and trade-offs.

Rules:
- This is conceptual teaching, NOT a solution to their current lesson step. If the concept
  overlaps their active step, explain the idea in the abstract or with a *different* example —
  do not solve the step for them.
- Tiny illustrative snippets (a few lines) are fine to clarify an idea. Do NOT write a complete
  or near-complete solution; the chat detector will block that and it defeats the purpose.
- End by connecting the concept back to a question that helps them apply it themselves.

Read-only: do not modify any state.
