#!/usr/bin/env python3
"""SessionStart hook (Layer 1 — soft).

If the current project has been initialized with `/learn` and Socratic mode is
on, inject the tutoring contract + a snapshot of the student's profile as
`additionalContext`. In uninitialized projects this stays silent, so the plugin
never interferes with normal coding work.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils"))
import state  # noqa: E402


SOCRATIC_CONTRACT = """\
# Claude Learn — Socratic Tutoring Mode is ACTIVE

You are a Socratic programming tutor for this student, not a code-writing assistant.
Your job is to make them think, not to hand them answers.

## Rules (non-negotiable)
- DO NOT write the student's code for them. File-writing tools are hard-blocked while
  learning mode is on; don't fight the block — guide instead.
- DO NOT paste complete or near-complete solutions into chat. Small illustrative
  snippets (a couple of lines) are fine when explaining a concept.
- Lead with questions that expose the next step in the student's reasoning.
- Use the 3-level hint ladder via `/hint`: (1) directional, (2) structural,
  (3) near-explicit/partial — never jump straight to level 3.
- Gate progress: a step is only complete when the student demonstrates understanding
  via `/check`. Never advance them on output-correctness alone.
- Calibrate depth to their level: low levels get analogies and concrete examples;
  high levels get trade-offs and edge cases.
- Feedback must be specific and earned — no vague encouragement.

You MAY freely read files, search, and research (Read/Grep/Glob/WebSearch) to give
better-informed guidance. Helping the student think is the goal."""


def profile_summary(profile):
    if not profile:
        return ""
    langs = ", ".join(f"{k} (lvl {v})" for k, v in (profile.get("languages") or {}).items())
    fws = ", ".join(f"{k} (lvl {v})" for k, v in (profile.get("frameworks") or {}).items())
    weak = ", ".join(profile.get("weakConcepts") or [])
    queue = profile.get("reinforcementQueue") or []
    lines = ["\n## This student's profile"]
    if langs:
        lines.append(f"- Languages: {langs}")
    if fws:
        lines.append(f"- Frameworks: {fws}")
    if weak:
        lines.append(f"- Known weak concepts: {weak}")
    if queue:
        top = max(queue, key=lambda q: q.get("priority", 0))
        lines.append(f"- Top reinforcement target: {top.get('concept')} (priority {top.get('priority')})")
    return "\n".join(lines) if len(lines) > 1 else ""


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}

    root = state.find_project_root(payload.get("cwd"))
    if not state.is_learning_active(root):
        sys.exit(0)  # silent in non-learning projects

    profile = state.load_profile(root)
    lesson = state.load_state(root)
    context = SOCRATIC_CONTRACT + profile_summary(profile)

    if lesson and lesson.get("topic"):
        context += (
            f"\n\n## Active lesson\n- Topic: {lesson['topic']} "
            f"({lesson.get('difficulty', 'intermediate')})\n"
            f"- On step {lesson.get('currentStep', 0) + 1} of {len(lesson.get('steps', []))}; "
            f"awaitingCheck={lesson.get('awaitingCheck', False)}.\n"
            "Resume from this step. Don't restart the lesson."
        )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
