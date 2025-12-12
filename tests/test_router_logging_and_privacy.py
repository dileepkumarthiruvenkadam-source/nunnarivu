# tests/test_router_logging_and_privacy.py

import json
from pathlib import Path

from backend import router


def test_route_message_logs_and_masks(tmp_path, monkeypatch):
    """
    - Ask LLM -> mocked to open Safari
    - Ensure:
      - route_message returns reply from open_app
      - interaction is logged
      - log contains latency_ms and slow
      - sensitive digits in user_text are masked
    """

    # 1) Fake ask_llm -> always choose open_app Safari
    def fake_ask_llm(messages):
        return json.dumps({
            "action": "open_app",
            "args": {"name": "safari"},
            "assistant_reply": "Opening Safari."
        })

    monkeypatch.setattr(router, "ask_llm", fake_ask_llm)

    # 2) Fake open_app -> don't actually open Safari
    def fake_open_app(name: str) -> str:
        return f"Opening {name}."

    monkeypatch.setattr(router, "open_app", fake_open_app)

    # 3) Redirect LOG_PATH to a temporary file
    log_file = tmp_path / "nunnarivu_interactions.jsonl"
    monkeypatch.setattr(router, "LOG_PATH", str(log_file))

    # 4) Call route_message with sensitive-ish content
    resp = router.route_message("my otp is 123456, open safari")

    # Response should come from fake_open_app
    assert "opening safari" in resp["assistant_reply"].lower()

    # Log file should now have 1 line
    content = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1

    entry = json.loads(content[0])
    assert "latency_ms" in entry
    assert "slow" in entry

    # Digits should be masked
    assert "123456" not in entry["user_text"]
    assert "******" in entry["user_text"]


def test_route_message_skips_very_sensitive(tmp_path, monkeypatch):
    """
    For commands like 'open my banking app', we expect router.log_interaction
    to skip logging entirely.
    """

    def fake_ask_llm(messages):
        return json.dumps({
            "action": "none",
            "args": {},
            "assistant_reply": "This is sensitive."
        })

    monkeypatch.setattr(router, "ask_llm", fake_ask_llm)

    log_file = tmp_path / "nunnarivu_interactions.jsonl"
    monkeypatch.setattr(router, "LOG_PATH", str(log_file))

    resp = router.route_message("open my banking app")
    assert "sensitive" in resp["assistant_reply"].lower()

    # Should skip logging -> file should not exist or be empty
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8").strip()
        assert content == "" or content == "\n"


def test_fast_path_open_app_is_logged(tmp_path, monkeypatch):
    """
    The fast 'open <app>' path should:
      - NOT call ask_llm
      - call open_app directly
      - still log the interaction
    """
    called = {"ask_llm": 0, "open_app": 0}

    def fake_ask_llm(messages):
        called["ask_llm"] += 1
        return json.dumps({
            "action": "none",
            "args": {},
            "assistant_reply": "LLM path"
        })

    def fake_open_app(name: str) -> str:
        called["open_app"] += 1
        return f"Opening {name}."

    monkeypatch.setattr(router, "ask_llm", fake_ask_llm)
    monkeypatch.setattr(router, "open_app", fake_open_app)

    log_file = tmp_path / "nunnarivu_interactions.jsonl"
    monkeypatch.setattr(router, "LOG_PATH", str(log_file))

    resp = router.route_message("open safari")

    assert "opening safari" in resp["assistant_reply"].lower()
    assert called["open_app"] == 1
    # Depending on implementation ask_llm may be 0 here (fast path)
    assert called["ask_llm"] == 0

    # Log should exist
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["assistant_action"]["action"] == "open_app"
    assert "safari" in entry["assistant_action"]["args"]["name"]