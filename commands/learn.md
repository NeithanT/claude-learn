---
description: Initialize the project's Socratic profile (no args) or start a guided lesson on a topic (/learn <topic> [beginner|intermediate|advanced])
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion, WebSearch
argument-hint: "[topic] [difficulty]"
---

Arguments: `$ARGUMENTS`

State lives in `.claude-learn/` at the project root: `profile.json` (knowledge profile)
and `state.json` (active lesson). These paths are write-allowed even in learning mode.

## If `$ARGUMENTS` is EMPTY → initialize the project profile

1. **Detect the stack.** Look for `package.json`, `requirements.txt`/`pyproject.toml`,
   `pom.xml`/`build.gradle`, `go.mod`, `Cargo.toml`, `Gemfile`, etc. Note the primary
   languages and frameworks. Don't write any code.
2. **Calibrate the student's level.** Use AskUserQuestion to ask 2–3 short questions that
   gauge their level (1–10) in each detected language/framework — e.g. how comfortable they
   are, what they've built, a concept self-rating. Keep it quick.
3. **Write `profile.json`** at `.claude-learn/profile.json` with: `socraticEnabled: true`,
   `languages` and `frameworks` maps of name→level (1–10), and empty `masteredConcepts`,
   `weakConcepts`, `reinforcementQueue` arrays.
4. **Persist Socratic mode** by writing/appending a short note to `.claude/CLAUDE.md` in the
   project: that this project uses Claude Learn (Socratic tutoring — hints not answers,
   gated progress, never write the student's code).
5. Confirm what you detected and the levels you recorded. From now on every session in this
   project is Socratic (the hooks enforce it).

## If `$ARGUMENTS` has a topic → start a guided lesson

Parse the topic and optional trailing difficulty (`beginner` | `intermediate` | `advanced`,
default `intermediate`).

1. **Generate a lesson plan** for the topic, calibrated to the difficulty and the student's
   profile level. Break it into ordered conceptual steps (roughly 4–8), each building on the
   last. Do NOT pre-write solution code.
2. **Offer an exercises folder.** Ask (AskUserQuestion) whether to create an `exercises/`
   folder with starter stubs + TODO markers (signatures and comments only — NO solutions) and
   any reference data the student needs. Writes under `exercises/` are allowed; create it only
   if they say yes.
3. **Write `state.json`** with: `topic`, `difficulty`, `steps` (the step descriptions),
   `currentStep: 0`, `completedSteps: []`, `hintsUsed: {}`, `awaitingCheck: false`,
   `stopRedoCount: 0`.
4. Present step 1 as a question that gets the student thinking. Tell them to use `/hint` if
   stuck and `/check` when they think they understand. Do not reveal later steps.
