#!/usr/bin/env python3
"""PreToolUse hook (Layer 2 — the hard block).

While learning mode is active, deny Claude's attempts to author the student's
code. This is the mechanical guarantee behind "never writes your code for you":

  - Edit / Write / MultiEdit / NotebookEdit : denied unless the target path is a
    carve-out (.claude-learn/, exercises/, or *.md).
  - Bash : denied only when the command writes code into a non-carved path via
    redirection (`>`, `>>`), `tee`, or `cp`/`mv`/`install`. Plain runs, tests,
    reads, git, etc. pass through untouched.

Read/Grep/Glob/WebFetch/WebSearch are never matched by this hook, so Claude keeps
full research ability. In uninitialized projects the hook allows everything.
"""

import json
import os
import re
import shlex
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "utils"))
import state  # noqa: E402


WRITE_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

DENY_REASON_FILE = (
    "Learning mode is on — you may not write the student's code for them. "
    "Instead, give the next hint on the /hint ladder (directional first) or ask a "
    "guiding question so THEY make the change. "
    "(Writes are still allowed under .claude-learn/, exercises/, and to .md files.)"
)

DENY_REASON_BASH = (
    "Learning mode is on — this command would write code into the student's project. "
    "Don't implement it for them; guide with a hint or a question instead. "
    "(Writes are still allowed under .claude-learn/, exercises/, and to .md files.)"
)

# Redirection / tee targets: `> file`, `>> file`, `tee file`, `tee -a file`.
REDIRECT_RE = re.compile(r"(?:>>?|\btee\b(?:\s+-a)?)\s+(\"[^\"]+\"|'[^']+'|[^\s;|&<>]+)")


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _looks_like_file(token):
    token = token.strip().strip("\"'")
    if not token or token.startswith(("&", "$", "/dev/")):
        return False
    return True


def bash_write_targets(command, cwd):
    """Best-effort extraction of paths a bash command writes to."""
    targets = []
    for m in REDIRECT_RE.finditer(command):
        tok = m.group(1).strip().strip("\"'")
        if _looks_like_file(tok):
            targets.append(tok)

    # cp / mv / install: destination is the last positional argument.
    for stmt in re.split(r"[;&|]+|\n", command):
        try:
            parts = shlex.split(stmt)
        except ValueError:
            continue
        if not parts:
            continue
        if parts[0] in ("cp", "mv", "install"):
            args = [p for p in parts[1:] if not p.startswith("-")]
            if len(args) >= 2 and _looks_like_file(args[-1]):
                targets.append(args[-1])

    resolved = []
    for t in targets:
        resolved.append(t if os.path.isabs(t) else os.path.join(cwd or os.getcwd(), t))
    return resolved


def main():
    try:
        payload = json.load(sys.stdin)
    except (ValueError, OSError):
        sys.exit(0)

    cwd = payload.get("cwd")
    root = state.find_project_root(cwd)
    if not state.is_learning_active(root):
        sys.exit(0)  # not a learning project — never interfere

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    if tool in WRITE_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if path and not state.is_write_allowed(path, root):
            deny(DENY_REASON_FILE)
        sys.exit(0)

    if tool == "Bash":
        command = tool_input.get("command", "") or ""
        for target in bash_write_targets(command, cwd):
            if not state.is_write_allowed(target, root):
                deny(DENY_REASON_BASH)
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
