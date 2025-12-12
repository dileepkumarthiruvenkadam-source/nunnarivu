# backend/mac_actions.py
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

from .discover_apps import load_app_index, APP_INDEX_PATH

# Simple in-memory cache so we don’t hit the disk every time
_APP_INDEX_CACHE: Dict[str, str] | None = None


def _get_app_index() -> Dict[str, str]:
    """
    Return a cached app index (name -> full path).
    If the cache is empty, load from disk (which will auto-rebuild if needed).
    """
    global _APP_INDEX_CACHE
    if _APP_INDEX_CACHE is None:
        _APP_INDEX_CACHE = load_app_index()
    return _APP_INDEX_CACHE


def _normalize(s: str) -> str:
    return s.strip().lower()


def _find_app_matches(query: str) -> List[Tuple[str, str]]:
    """
    Find all apps whose normalized name matches the query in a flexible way:
      - exact match
      - startswith
      - substring
    No hardcoding of specific app names — purely index-driven.
    """
    index = _get_app_index()
    q = _normalize(query)

    # Exact key match
    if q in index:
        return [(q, index[q])]

    matches: List[Tuple[str, str]] = []

    for name, path in index.items():
        n = _normalize(name)
        if n == q:
            matches.append((name, path))
        elif n.startswith(q):
            matches.append((name, path))
        elif q in n:
            matches.append((name, path))

    return matches


def _filter_primary_apps(matches: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    From a list of (name, path) matches, prefer "primary" apps:
      - NOT internal helpers inside some other .app bundle
        (paths containing '.app/Contents/')
      - NOT obvious helper apps ('helper' in the name)
    If at least one primary app exists, return only those.
    Otherwise, return the original list.
    This stays generic and works for all Macs.
    """
    if not matches:
        return matches

    primary: List[Tuple[str, str]] = []
    helpers: List[Tuple[str, str]] = []

    for name, path in matches:
        p = path.lower()
        n = name.lower()

        is_internal = ".app/contents/" in p
        is_helper_name = "helper" in n

        if is_internal or is_helper_name:
            helpers.append((name, path))
        else:
            primary.append((name, path))

    # If we found at least one "real" app, prefer that set
    if primary:
        return primary

    # Fallback: everything (e.g. in weird setups where everything looks like a helper)
    return matches


def open_app(name: str) -> str:
    """
    Open an application by (fuzzy) name.

    Behaviour:
      - Look up in the dynamic app index (no hardcoding).
      - If no match: clear error message.
      - If one primary match: open it.
      - If several primary matches: ask user to clarify.
      - Internal helpers (like 'Google Chrome Helper') are automatically
        down-ranked so 'open chrome' opens 'Google Chrome', not the helpers.
    """
    query = name.strip()
    if not query:
        return "Please tell me which app to open."

    matches = _find_app_matches(query)
    matches = _filter_primary_apps(matches)

    if not matches:
        return f"Sorry, I couldn't find an app called '{query.lower()}'."

    # Single unambiguous match -> just open it
    if len(matches) == 1:
        app_name, app_path = matches[0]
        try:
            subprocess.run(["open", app_path], check=False)
            # Use the "pretty" name from the .app
            pretty = app_name.strip()
            return f"Opening {pretty}."
        except Exception as e:
            return f"Something went wrong trying to open {app_name}: {e}"

    # More than one real app: disambiguate
    names_list = ", ".join(sorted(n for n, _ in matches))
    example_name = matches[0][0]
    return (
        f"I found several apps matching '{query.lower()}': {names_list}. "
        f"Please say or type the full name, for example: 'open {example_name}'"
    )


def set_volume(level: int) -> str:
    """
    Set system output volume (0–100).

    Uses AppleScript via `osascript`. No hardcoded app names, just settings.
    """
    try:
        lvl = int(level)
    except (TypeError, ValueError):
        return "Please give me a volume level between 0 and 100."

    if not (0 <= lvl <= 100):
        return "Volume level must be between 0 and 100."

    # macOS volume: 0–100
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f"set volume output volume {lvl}"
            ],
            check=False,
        )
        return f"Setting volume to {lvl}."
    except Exception as e:
        return f"Something went wrong setting the volume: {e}"


def open_folder(path: str) -> str:
    """
    Open a folder in Finder.

    Again, no hardcoded paths — the router / LLM decides the path string.
    """
    if not path:
        return "Please tell me which folder to open."

    expanded = str(Path(path).expanduser())
    try:
        subprocess.run(["open", expanded], check=False)
        return f"Opening your folder: {expanded}"
    except Exception as e:
        return f"Something went wrong opening the folder: {e}"