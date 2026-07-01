"""Shared state helpers for the Claude Learn plugin.

All hooks and commands read/write the student's learning state through this module.
State lives in `.claude-learn/` inside the student's project:

  - profile.json : always-on knowledge profile (Layer 1)
  - state.json   : active lesson state (Layer 2)

These files are written here directly (not via Claude's Edit/Write tool), so the
hard-block hook never fights the plugin's own bookkeeping.
"""

import json
import os
import tempfile

LEARN_DIR_NAME = ".claude-learn"
PROFILE_FILE = "profile.json"
STATE_FILE = "state.json"

# Paths Claude IS still allowed to write while learning mode is active.
# Anything else under the project is denied by pre_tool_use.py.
EXERCISES_DIR_NAME = "exercises"
ALLOWED_WRITE_SUFFIXES = (".md",)


def find_project_root(start=None):
    """Walk up from `start` (or cwd) looking for a `.claude-learn/` directory.

    Returns the directory that contains `.claude-learn/`. If none is found,
    returns the starting directory (so an uninitialized project resolves to cwd
    and `is_learning_active` will report False there).
    """
    cur = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.isdir(os.path.join(cur, LEARN_DIR_NAME)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:  # reached filesystem root
            return os.path.abspath(start or os.getcwd())
        cur = parent


def learn_dir(root):
    return os.path.join(root, LEARN_DIR_NAME)


def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError, OSError):
        return None


def _atomic_write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def default_profile():
    return {
        "socraticEnabled": True,
        "languages": {},
        "frameworks": {},
        "masteredConcepts": [],
        "weakConcepts": [],
        "reinforcementQueue": [],
    }


def default_state():
    return {
        "topic": None,
        "difficulty": "intermediate",
        "steps": [],
        "currentStep": 0,
        "currentPhase": "mini_lesson",
        "completedSteps": [],
        "hintsUsed": {},
        "awaitingCheck": False,
        "lastEvaluation": None,
        "stopRedoCount": 0,
    }


def load_profile(root):
    return _load_json(os.path.join(learn_dir(root), PROFILE_FILE))


def save_profile(root, data):
    _atomic_write_json(os.path.join(learn_dir(root), PROFILE_FILE), data)


def load_state(root):
    return _load_json(os.path.join(learn_dir(root), STATE_FILE))


def save_state(root, data):
    _atomic_write_json(os.path.join(learn_dir(root), STATE_FILE), data)


def is_learning_active(root):
    """True iff the project has been initialized and Socratic mode is enabled."""
    profile = load_profile(root)
    return bool(profile) and bool(profile.get("socraticEnabled", False))


def is_write_allowed(path, root):
    """Carve-outs: writes Claude may still perform while learning mode is on.

    Allowed: anything under `.claude-learn/`, anything under `exercises/`
    (student scaffolding/stubs), and Markdown files. Everything else = denied.
    """
    if not path:
        return False
    ap = os.path.abspath(path)
    learn = os.path.abspath(learn_dir(root)) + os.sep
    exercises = os.path.abspath(os.path.join(root, EXERCISES_DIR_NAME)) + os.sep
    if ap.startswith(learn) or ap.startswith(exercises):
        return True
    if ap.lower().endswith(ALLOWED_WRITE_SUFFIXES):
        return True
    return False
