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

**Testing locally without publishing?** Clone the repo and point Claude Code at it directly:

```
git clone https://github.com/NeithanT/claude-learn.git
claude --plugin-dir ./claude-learn
```

## Two Layers of Learning

**Layer 1 — Project Profile** (always-on). Run `/learn` once in a project. The plugin detects your stack, profiles your current knowledge level per language/framework, and from that point on every coding conversation in the project is Socratic. Claude calibrates its guidance to your level and tracks the concepts you struggle with. Progress is saved across sessions.

**Layer 2 — Topic Lessons** (on-demand). `/learn <topic>` starts a structured, step-by-step lesson plan. You can't advance to the next step without demonstrating genuine understanding via `/check`. Claude will also offer to scaffold an `exercises/` folder with any starter files or data the lesson needs. Progress is saved across sessions.

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

## Commands

| Command | Description |
|---------|-------------|
| `/learn` | Initialize project profile — detects stack, sets knowledge levels |
| `/learn <topic> [difficulty]` | Start a guided lesson. Difficulty: `beginner`, `intermediate` (default), `advanced` |
| `/hint` | Get the next hint (1st time: directional, 2nd time: structural, 3rd time: near-explicit or partial solution) |
| `/check` | Submit your understanding for evaluation — gates step progression |
| `/progress` | See your knowledge profile, active lesson status, and reinforcement queue |
| `/explain <concept>` | Get a concept explained without solving your current step |
| `/reinforce` | Targeted session on your highest-priority weak concept |

## What Claude Will and Won't Do

**Will do:**
- Ask questions that guide your thinking (Socratic method)
- Calibrate depth to your knowledge level (beginner gets analogies; advanced gets trade-offs)
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

## State Files

Both files live in `.claude-learn/` inside your project directory:

- `profile.json` — knowledge profile: languages, frameworks, levels, mastered/weak concepts, reinforcement queue
- `state.json` — active lesson state: current topic, step, hints used, completed steps

A `.claude/CLAUDE.md` is also written to the project to make Socratic mode persistent across all sessions.
