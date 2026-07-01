#!/usr/bin/env python3
"""UserPromptSubmit hook (Layer 1 — soft).

Re-injects a short Socratic reminder each turn, and — when the student's prompt
looks like a demand for the answer ("just give me the code", "write it for me",
"what's the solution") — injects an explicit instruction to refuse and offer a
hint instead. Stays silent in uninitialized projects.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils"))
import state  # noqa: E402


# Phrases that signal "stop teaching, just hand it over".
ANSWER_DEMAND = re.compile(
    r"\b(just (give|tell|show) me|write (it|the code|this) for me|"
    r"give me the (answer|code|solution)|do it for me|"
    r"what'?s the (answer|solution)|complete the code|finish (it|the code)|"
    r"stop asking|just fix it)\b",
    re.IGNORECASE,
)

REMINDER = (
    "[Claude Learn] Socratic mode is on: guide with questions and the /hint ladder; "
    "do not write the student's code or paste complete solutions. Keep the CS50-style "
    "warm, friendly voice — one small concrete question at a time, analogies before "
    "jargon, no stacked sub-questions."
)

REFUSAL = (
    "[Claude Learn] The student is asking you to just hand over the answer. "
    "Do NOT comply. Acknowledge the urge, then give the next hint on the /hint "
    "ladder (directional first) and one guiding question. The goal is for THEM to "
    "produce the code."
)


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        payload = {}

    root = state.find_project_root(payload.get("cwd"))
    if not state.is_learning_active(root):
        sys.exit(0)

    prompt = payload.get("prompt", "") or ""
    context = REMINDER
    if ANSWER_DEMAND.search(prompt):
        context += "\n\n" + REFUSAL

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
