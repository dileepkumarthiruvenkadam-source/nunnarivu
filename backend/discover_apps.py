# backend/discover_apps.py

import os
import json
from pathlib import Path
from typing import Dict, Optional

APP_INDEX_PATH = Path(__file__).with_name("app_index.json")


def _iter_app_bundles() -> Dict[str, str]:
    """
    Walk standard macOS application locations and yield .app bundles.

    We do NOT hard-code any specific app names. Everything is discovered
    dynamically from the filesystem.
    """
    roots = [
        "/Applications",
        "/System/Applications",
        "/System/Library/CoreServices",
        str(Path.home() / "Applications"),
    ]

    seen: Dict[str, str] = {}
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue

        for entry in root_path.rglob("*.app"):
            if not entry.is_dir():
                continue

            # Canonical name = bundle name without .app, lowercased
            name = entry.stem.strip().lower()
            # Only keep the first path we see for a given name (stable enough)
            if name not in seen:
                seen[name] = str(entry)

    return seen


def rebuild_app_index(index_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Rebuild the app index JSON file by scanning the filesystem.
    Returns the dict {normalized_name: full_path}.
    """
    if index_path is None:
        index_path = APP_INDEX_PATH

    apps = _iter_app_bundles()
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)

    print(f"[OK] Discovered {len(apps)} apps.")
    print(f"[OK] Written to: {index_path}")
    return apps


def load_app_index(index_path: Optional[Path] = None) -> Dict[str, str]:
    """
    Load the app index. If missing or corrupted, rebuild automatically.
    """
    if index_path is None:
        index_path = APP_INDEX_PATH

    if not index_path.exists():
        print("[WARN] app_index.json missing — rebuilding.")
        return rebuild_app_index(index_path=index_path)

    try:
        with index_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("app_index is not a JSON object")
        return data
    except Exception:
        print("[WARN] app_index.json is invalid — rebuilding.")
        return rebuild_app_index(index_path=index_path)


if __name__ == "__main__":
    # Manual CLI:
    #   python backend/discover_apps.py
    load_app_index()