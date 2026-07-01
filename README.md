# Claude Learn

A Claude Code plugin that turns AI assistance into genuine learning. Instead of giving you the answer, it asks the questions that get you there.

## The Problem

When students ask AI for answers, they get answers — but they don't learn. Claude Learn flips this: the AI asks questions, the student does the thinking.

## The No-Cheating Rule

Under no circumstances will the AI write code or hand over a complete solution. It will help you debug, offer hints, and point you in the right direction — but it will never do the thinking for you.

## Installation

```
/plugin marketplace add NeithanT/claude-learn
/plugin install claude-learn@claude-learn-marketplace
```

That's it — the commands and hooks are active immediately.

**Note on command names:** Claude Code always namespaces plugin commands as
`/<plugin-name>:<command-name>` to avoid collisions between plugins (this is true both via
`--plugin-dir` and after a marketplace install — it's not a quirk of local testing). So invoke
commands as `/claude-learn:learn`, `/claude-learn:hint`, `/claude-learn:check`, etc. — the bare
`/learn` form won't resolve.

**Testing locally without publishing?** Clone the repo and point Claude Code at it directly:

```
git clone https://github.com/NeithanT/claude-learn.git
claude --plugin-dir ./claude-learn
```

## Two Layers of Learning

**Layer 1 — Project Profile** (always-on). Run `/learn` once in a project. The plugin detects your stack, profiles your current knowledge level per language/framework, and from that point on every coding conversation in the project is Socratic. Claude calibrates its guidance to your level and tracks the concepts you struggle with. Progress is saved across sessions.

**Layer 2 — Topic Lessons** (on-demand). `/learn <topic>` starts a structured, step-by-step lesson plan. Each step runs a two-phase cycle that repeats all the way through the plan:

1. **Mini Lesson** — Claude teaches the concept directly: a short, warm explanation with an everyday analogy, before any question is asked.
2. **Problem Solving** — Claude poses a Socratic question that makes you apply what you just learned. You can't advance to the next step without demonstrating genuine understanding via `/check`.

Then it repeats: Mini Lesson for the next step, Problem Solving for the next step, and so on. Claude will also offer to scaffold an `exercises/` folder with any starter files or data the lesson needs. Progress (including which phase you're in) is saved across sessions.

Both layers track what you know per topic on a 1–10 scale and steer you toward your weakest areas.

## Getting Started

```
# In any project directory:
/learn
```

Claude will detect your stack (Java, Python, React, etc.), ask a few quick questions to gauge your level, and write a knowledge profile. From then on, it's always in tutoring mode for that project.

```
# Start a lesson on a specific topic:
/learn dependency injection beginner
/learn react hooks
/learn binary search trees advanced
```

To set difficulty, include the word `beginner`, `intermediate`, or `advanced` anywhere in
the command (it's pulled out as a whole word, so it won't get confused with similar-looking
topic words). If you leave it out, Claude infers it from your profile level for that
language/framework, or asks you directly rather than silently guessing `intermediate`.

## Commands

| Command | Description |
|---------|-------------|
| `/learn` | Initialize project profile — detects stack, sets knowledge levels |
| `/learn <topic> [difficulty]` | Start a guided lesson. Difficulty: `beginner`, `intermediate`, `advanced` — inferred from your profile or asked if omitted |
| `/hint` | Get the next hint (1st time: directional, 2nd time: structural, 3rd time: near-explicit or partial solution). Only applies once you're in the Problem Solving phase |
| `/check` | Submit your understanding for evaluation — gates step progression. Only applies once you're in the Problem Solving phase |
| `/progress` | See your knowledge profile, active lesson status, and reinforcement queue |
| `/explain <concept>` | Get a concept explained without solving your current step |
| `/reinforce` | Targeted session on your highest-priority weak concept |

## What Claude Will and Won't Do

**Will do:**
- Teach each new concept directly in a short Mini Lesson before asking you to apply it
- Ask questions that guide your thinking (Socratic method) during Problem Solving — one
  small question at a time, in a warm, CS50-style teaching voice
- Calibrate depth to your knowledge level (beginner gets everyday analogies and plain
  language; advanced gets trade-offs and edge cases)
- Give progressively more specific hints — never the full answer
- Evaluate whether you *understand* (not just whether output is correct)
- Track weak concepts and surface them for reinforcement
- Resume lessons and profile across sessions

**Won't do:**
- Write your code for you
- Give the answer when asked directly
- Let you advance without demonstrating understanding
- Use vague encouragement — only specific, earned feedback

## How the "no answers" rule is enforced

Claude Learn doesn't just *ask* the model to behave — it enforces the rule with three layers
of hooks (in `hooks/`):

1. **Soft layer (behavioral).** `SessionStart` and `UserPromptSubmit` hooks inject the Socratic
   contract every session and every turn. If you ask Claude to "just give me the code", the
   prompt hook detects it and tells Claude to refuse and hint instead.
2. **Hard layer (mechanical).** A `PreToolUse` hook **denies** Claude's file-writing tools
   (`Edit`/`Write`/`MultiEdit`/`NotebookEdit`, and code-writing `Bash` like `echo … > file.py`)
   while learning mode is active. Claude literally cannot author your code. Carve-outs: it may
   still write under `.claude-learn/`, under `exercises/` (starter stubs for *you* to fill in),
   and to `.md` files. Reading, searching, and web research are **never** blocked — Claude keeps
   full ability to gather insight to help you.
3. **Detector layer.** A `Stop` hook scans Claude's reply for a full code block; if it tried to
   paste a near-complete solution into chat, it's forced to redo the turn as a hint. (This layer
   is heuristic — line-count on fenced blocks — so it catches obvious solution dumps, not
   cleverly fragmented ones. Layers 1–2 carry the hard guarantee for *files*; this is best-effort
   for *chat text*. A loop guard releases after two redos so you're never stuck.)

The plugin only enforces in projects that have run `/learn` (where `.claude-learn/profile.json`
exists). In any other project the hooks stay silent and don't interfere.

## Known Limitation: Terminal Autocomplete

Some terminals and shells offer ghost-text or history-based autosuggestions as you type —
ahead of what you've actually typed, they'll show a plausible completion pulled from prior
input. During a Socratic exchange, this can pre-fill a guessable answer into the prompt box
before you've worked it out yourself, which undercuts the whole point of the exercise.

This is outside the plugin's control. `claude-learn`'s hooks (`SessionStart`,
`UserPromptSubmit`, `PreToolUse`, `Stop`) only run on submit or tool-use — there's no hook
that fires at keystroke time, so the plugin has no way to intercept or suppress
autosuggested text before you send it.

If you use a shell autosuggestion plugin (e.g. `zsh-autosuggestions`, fish's built-in
suggestions), consider disabling it — or simply avoid pressing Tab/→/End to accept ghost
text — while working through a lesson, so you only ever submit what you actually typed.

## State Files

Both files live in `.claude-learn/` inside your project directory:

- `profile.json` — knowledge profile: languages, frameworks, levels, mastered/weak concepts, reinforcement queue
- `state.json` — active lesson state: current topic, step, phase (`mini_lesson` or `problem_solving`), hints used, completed steps

A `.claude/CLAUDE.md` is also written to the project to make Socratic mode persistent across all sessions.
