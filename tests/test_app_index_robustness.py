# tests/test_app_index_robustness.py

import json
from pathlib import Path

from backend import mac_actions
from backend.discover_apps import APP_INDEX_PATH, rebuild_app_index, load_app_index


def test_load_app_index_missing(tmp_path, monkeypatch):
    """
    If the index file is missing, load_app_index should NOT crash.
    It should rebuild (or return an empty dict) and create the file.
    """
    fake_index = tmp_path / "app_index.json"
    if fake_index.exists():
        fake_index.unlink()

    monkeypatch.setattr("backend.discover_apps.APP_INDEX_PATH", fake_index)

    index = load_app_index()

    assert isinstance(index, dict)
    assert fake_index.exists()


def test_load_app_index_corrupt(tmp_path, monkeypatch):
    """
    If the index file is corrupted, load_app_index should rebuild it.
    """
    fake_index = tmp_path / "app_index.json"
    fake_index.write_text("this is not json", encoding="utf-8")

    monkeypatch.setattr("backend.discover_apps.APP_INDEX_PATH", fake_index)

    index = load_app_index()
    assert isinstance(index, dict)
    assert fake_index.exists()
    # ensure it's valid JSON now
    data = json.loads(fake_index.read_text(encoding="utf-8"))
    assert isinstance(data, dict)