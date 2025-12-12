# tools/dev_notes.py
"""
Small helper to append timestamped dev notes.

Usage:
    source venv/bin/activate
    python tools/dev_notes.py "Implemented universal app discovery for macOS apps"

This will append a line like:
    - [2025-12-06 01:23:45] Implemented universal app discovery for macOS apps
to dev_notes.md in the project root.
"""

import os
import sys
from datetime import datetime

# Dev notes file in project root
NOTES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "dev_notes.md",
)

def ensure_header():
    """Create the file with a header if it doesn't exist yet."""
    if not os.path.exists(NOTES_PATH):
        with open(NOTES_PATH, "w", encoding="utf-8") as f:
            f.write("# Nunnarivu — Dev Notes\n\n")
            f.write("_Auto-appended notes about changes, experiments and ideas._\n\n")


def append_note(text: str):
    """Append a timestamped note line."""
    ensure_header()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"- [{ts}] {text}\n"
    with open(NOTES_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"[OK] Added note to {NOTES_PATH}:\n{line.strip()}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/dev_notes.py \"your note text here\"")
        sys.exit(1)

    text = " ".join(sys.argv[1:]).strip()
    if not text:
        print("Error: empty note text.")
        sys.exit(1)

    append_note(text)


if __name__ == "__main__":
    main()
