# backend/app_aliases.py

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

APP_INDEX_PATH = os.path.join(os.path.dirname(__file__), "app_index.json")


def _normalize(text: str) -> str:
    """Lowercase, strip, collapse spaces."""
    return " ".join(text.lower().strip().split())


def load_app_index() -> Dict[str, str]:
    """
    Load the discovered applications.

    The JSON is expected to be:
        {
          "visual studio code": "/Applications/Visual Studio Code.app",
          "google chrome": "/Applications/Google Chrome.app",
          ...
        }

    Keys are normalized app "display names" (lowercased).
    """
    if not os.path.exists(APP_INDEX_PATH):
        return {}

    with open(APP_INDEX_PATH, "r") as f:
        data = json.load(f)

    # ensure keys are normalized
    return {_normalize(name): path for name, path in data.items()}


def resolve_app_candidates(user_query: str) -> List[str]:
    """
    Given a user phrase like:

      - 'microsoft'
      - 'google'
      - 'visual'
      - 'code'

    return a list of *display names* that match, e.g.:

      ['Microsoft Word', 'Microsoft Excel', 'Microsoft PowerPoint']

    The matching is purely data-driven from app_index.json.
    No app names are hardcoded.
    """
    query = _normalize(user_query)
    if not query:
        return []

    index = load_app_index()
    candidates: List[str] = []

    for norm_name in index.keys():
        full = norm_name  # already normalized
        words = full.split()

        # full match
        if query == full:
            candidates.append(full)
            continue

        # query matches a whole word exactly: "chrome" in "google chrome"
        if query in words:
            candidates.append(full)
            continue

        # query is a prefix of the full name: "google" -> "google chrome"
        if full.startswith(query + " "):
            candidates.append(full)
            continue

        # query is a prefix of any word: "vis" -> "visual studio code"
        if any(w.startswith(query) for w in words):
            candidates.append(full)
            continue

    # deduplicate while preserving order
    seen = set()
    unique: List[str] = []
    for name in candidates:
        if name not in seen:
            seen.add(name)
            unique.append(name)

    return unique


def get_app_path(display_name: str) -> Optional[str]:
    """
    Given a (possibly not-normalized) display name, return the app path,
    or None if not found.
    """
    index = load_app_index()
    norm = _normalize(display_name)
    return index.get(norm)