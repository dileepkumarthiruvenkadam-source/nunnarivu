# tests/test_open_app_behavior.py

from backend import mac_actions


def test_score_match_basic():
    # Simple non-zero scores for related names
    assert mac_actions._score_match("safari", "safari") > 90
    assert mac_actions._score_match("chrome", "google chrome") >= 70
    assert mac_actions._score_match("studio", "visual studio code") >= 60


def test_find_app_candidates_simple(monkeypatch):
    """
    _find_app_candidates should prioritize better matches.
    """
    fake_index = {
        "google chrome": "/Applications/Google Chrome.app",
        "visual studio code": "/Applications/Visual Studio Code.app",
        "safari": "/Applications/Safari.app",
    }

    # Direct query
    cands = mac_actions._find_app_candidates("safari", fake_index)
    assert cands[0][1] == "safari"

    # Partial query
    cands = mac_actions._find_app_candidates("chrome", fake_index)
    names = [c[1] for c in cands]
    assert names[0] == "google chrome"


def test_open_app_ambiguous(monkeypatch):
    """
    If multiple apps match similarly, open_app should ask for clarification
    instead of guessing.
    """
    fake_index = {
        "microsoft word": "/Applications/Microsoft Word.app",
        "microsoft excel": "/Applications/Microsoft Excel.app",
        "microsoft outlook": "/Applications/Microsoft Outlook.app",
    }

    def fake_load_index(_=None):
        return fake_index

    monkeypatch.setattr(mac_actions, "load_app_index", fake_load_index)

    msg = mac_actions.open_app("microsoft")
    assert "several apps matching" in msg.lower()
    assert "microsoft word" in msg.lower()