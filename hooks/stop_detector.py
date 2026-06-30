#!/usr/bin/env python3
"""Stop hook (Layer 3 — the chat-solution detector).

Hooks can block file writes but cannot stop Claude from *typing* a full solution
into the chat. So when Claude finishes a turn, we inspect its last message: if it
contains a fenced code block longer than the threshold (a likely solution dump)
while learning mode is on, we block the stop and force Claude to redo the turn as
a hint instead.

This is heuristic (line-count on fenced blocks), not semantic — it catches obvious
dumps, not cleverly fragmented ones. A loop guard releases after MAX_REDOS so the
student is never hard-stuck.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils"))
import state  # noqa: E402


CODE_LINE_THRESHOLD = 8     # fenced blocks longer than this look like a solution
MAX_REDOS = 2               # release after this many consecutive forced redos

FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)

BLOCK_REASON = (
    "[Claude Learn] Your reply contains a near-complete code solution ({n} lines in a "
    "code block). That defeats the point — the student must write the code. Redo your "
    "response: remove the solution, give a directional hint plus one guiding question, "
    "and let them implement it. Small illustrative snippets (a few lines) are fine."
)


def last_assistant_text(transcript_path):
    """Return the text of the most recent assistant message in the JSONL transcript."""
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (FileNotFoundError, OSError):
        return ""

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            evt = json.loads(line)
        except ValueError:
            continue
        msg = evt.get("message", evt)
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                b.get("text", "") for b in content
                if isinstance(b, dict) and b.get("type") == "text"
            )
    return ""


def longest_code_block(text):
    longest = 0
    for m in FENCE_RE.finditer(text):
        body = m.group(1)
        n = len([ln for ln in body.splitlines() if ln.strip()])
        longest = max(longest, n)
    return longest


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        sys.exit(0)

    root = state.find_project_root(payload.get("cwd"))
    if not state.is_learning_active(root):
        sys.exit(0)

    lesson = state.load_state(root) or state.default_state()
    text = last_assistant_text(payload.get("transcript_path", ""))
    n = longest_code_block(text)

    if n <= CODE_LINE_THRESHOLD:
        # Clean turn — reset the consecutive-redo counter.
        if lesson.get("stopRedoCount"):
            lesson["stopRedoCount"] = 0
            state.save_state(root, lesson)
        sys.exit(0)

    redos = lesson.get("stopRedoCount", 0)
    if redos >= MAX_REDOS:
        # Loop guard: let it through so the student isn't hard-stuck.
        lesson["stopRedoCount"] = 0
        state.save_state(root, lesson)
        sys.exit(0)

    lesson["stopRedoCount"] = redos + 1
    state.save_state(root, lesson)
    print(json.dumps({"decision": "block", "reason": BLOCK_REASON.format(n=n)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
