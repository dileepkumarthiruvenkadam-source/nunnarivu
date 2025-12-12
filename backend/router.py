# backend/router.py

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict

from .llm_client import ask_llm
from .mac_actions import open_app, set_volume, open_folder
from .shell_actions import run_shell_command
from .cover_letter import generate_cover_letter

LOG_PATH = os.path.expanduser("~/nunnarivu/logs/nunnarivu_interactions.jsonl")

# Keywords that mean we should NOT log the raw text at all
VERY_SENSITIVE_KEYWORDS = [
    "bank",
    "banking",
    "keychain",
    "password manager",
]


def mask_sensitive_text(text: str) -> str:
    """
    Mask obviously sensitive patterns (e.g. long digit sequences like OTPs).
    We DO log these, but in masked form.
    """
    # Replace any 4+ digit sequence by ******.
    return re.sub(r"\d{4,}", "******", text)


def is_very_sensitive(text: str) -> bool:
    """
    For some commands (banking, keychain, etc.), we skip logging entirely.
    """
    lower = text.lower()
    return any(kw in lower for kw in VERY_SENSITIVE_KEYWORDS)


def log_interaction(
    user_text: str,
    assistant_action: Dict[str, Any],
    assistant_reply: str,
    latency_ms: float,
    slow: bool,
) -> None:
    """
    Append each interaction to a JSONL file for future training.
    """
    entry = {
        "timestamp": time.time(),
        "user_text": user_text,
        "assistant_action": assistant_action,
        "assistant_reply": assistant_reply,
        "latency_ms": latency_ms,
        "slow": slow,
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def maybe_log_interaction(
    raw_user_text: str,
    assistant_action: Dict[str, Any],
    assistant_reply: str,
    started_at: float,
) -> None:
    """
    Apply privacy rules + latency calculation before logging.
    """
    latency_ms = (time.time() - started_at) * 1000.0
    slow = latency_ms > 1000.0  # > 1 second considered slow

    if is_very_sensitive(raw_user_text):
        # For very sensitive commands we skip logging completely.
        print("[INFO] Skipping log for potentially sensitive command.")
        return

    safe_text = mask_sensitive_text(raw_user_text)
    log_interaction(safe_text, assistant_action, assistant_reply, latency_ms, slow)


def _parse_action_json(raw: str) -> Dict[str, Any]:
    """
    Try to parse the LLM output as JSON.

    Strategy:
    1. First, try direct json.loads(raw).
    2. If that fails, scan for the FIRST balanced {...} block and parse that.
    3. If everything fails, return a dict treating raw as plain text:
       {"assistant_reply": raw}
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    start = raw.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(raw[start:], start=start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    fragment = raw[start : i + 1]
                    try:
                        return json.loads(fragment)
                    except json.JSONDecodeError:
                        break

    return {"assistant_reply": raw}


def route_message(user_text: str) -> Dict[str, Any]:
    """
    High-level router: given raw user text, decide what to do.

    For speed:
    - Simple 'open ...' commands go through a FAST PATH (no LLM).
    - Everything else goes through the LLM action JSON protocol.
    """
    started_at = time.time()
    normalized = user_text.strip().lower()

    # ---------- FAST PATH: "open <something>" ----------

    if normalized.startswith("open "):
        # Respect privacy rules: very sensitive "open my banking app" still
        # goes to the LLM path (and can skip logging).
        if not is_very_sensitive(normalized):
            app_query = normalized[len("open ") :].strip()
            reply = open_app(app_query)

            maybe_log_interaction(
                raw_user_text=user_text,
                assistant_action={"action": "open_app", "args": {"name": app_query}},
                assistant_reply=reply,
                started_at=started_at,
            )
            return {"assistant_reply": reply}

    # ---------- LLM PATH ----------

    system_prompt = (
        "You are Sunny, an AI OS assistant for macOS. "
        "Your job is to map user requests to JSON actions.\n\n"
        "Valid actions:\n"
        "  open_app:       {\"name\": \"Safari\"}\n"
        "  set_volume:     {\"level\": 0-100}\n"
        "  open_folder:    {\"path\": \"~/Downloads\"}\n"
        "  run_shell:      {\"command\": \"ls -la\"}\n"
        "  create_cover_letter: {\"url\": \"https://...\", \"name\": \"Applicant\"}\n"
        "  none:           {} (just answer in natural language)\n\n"
        "You MUST respond ONLY with a single JSON object, no extra text.\n"
        "The JSON must always have at least these keys:\n"
        "  \"action\": \"open_app\" | \"set_volume\" | \"open_folder\" | \"run_shell\" | "
        "\"create_cover_letter\" | \"none\"\n"
        "  \"args\":   an object with arguments for that action (or {})\n"
        "  \"assistant_reply\": a short natural-language reply to the user.\n"
        "If the user only greets you (e.g. 'hey', 'hi'), use action 'none'."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]

    raw = ask_llm(messages)
    action_obj = _parse_action_json(raw)

    # Special case: model returned just {"none": {}} or similar
    if set(action_obj.keys()) == {"none"}:
        assistant_reply = "Hi, I'm Sunny. How can I help you?"
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "none", "args": {}},
            assistant_reply=assistant_reply,
            started_at=started_at,
        )
        return {"assistant_reply": assistant_reply}

    # Plain-text reply only
    if "action" not in action_obj and "assistant_reply" in action_obj:
        assistant_reply = action_obj["assistant_reply"]
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "none", "args": {}},
            assistant_reply=assistant_reply,
            started_at=started_at,
        )
        return {"assistant_reply": assistant_reply}

    action = action_obj.get("action", "none")
    args = action_obj.get("args", {}) or {}
    assistant_reply = action_obj.get("assistant_reply", "")

    # ---------- Execute mapped action ----------

    if action == "open_app":
        name = args.get("name", "")
        reply = open_app(name)
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "open_app", "args": {"name": name}},
            assistant_reply=reply,
            started_at=started_at,
        )
        return {"assistant_reply": reply}

    if action == "set_volume":
        level = args.get("level")
        reply = set_volume(level)
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "set_volume", "args": {"level": level}},
            assistant_reply=reply,
            started_at=started_at,
        )
        return {"assistant_reply": reply}

    if action == "open_folder":
        path = args.get("path", "~/")
        reply = open_folder(path)
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "open_folder", "args": {"path": path}},
            assistant_reply=reply,
            started_at=started_at,
        )
        return {"assistant_reply": reply}

    if action == "run_shell":
        command = args.get("command", "")
        code, out, err = run_shell_command(command)
        reply = f"Command exit code: {code}\n\nstdout:\n{out}\n\nstderr:\n{err}"
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "run_shell", "args": {"command": command}},
            assistant_reply=reply,
            started_at=started_at,
        )
        return {"assistant_reply": reply}

    if action == "create_cover_letter":
        job_url = args.get("url")
        name = args.get("name", "Applicant")
        if not job_url:
            assistant_reply = "I need a job URL to create a cover letter."
            maybe_log_interaction(
                raw_user_text=user_text,
                assistant_action={"action": "create_cover_letter", "args": args},
                assistant_reply=assistant_reply,
                started_at=started_at,
            )
            return {"assistant_reply": assistant_reply}

        try:
            path = generate_cover_letter(job_url, applicant_name=name)
            assistant_reply = f"Your cover letter is ready at:\n{path}"
        except Exception as e:
            assistant_reply = f"Something went wrong creating the cover letter: {e}"

        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": "create_cover_letter", "args": args},
            assistant_reply=assistant_reply,
            started_at=started_at,
        )
        return {"assistant_reply": assistant_reply}

    # default / none: just treat as normal reply
    if assistant_reply:
        maybe_log_interaction(
            raw_user_text=user_text,
            assistant_action={"action": action, "args": args},
            assistant_reply=assistant_reply,
            started_at=started_at,
        )
        return {"assistant_reply": assistant_reply}

    # Last fallback: show raw text, but still log
    maybe_log_interaction(
        raw_user_text=user_text,
        assistant_action={"action": action, "args": args},
        assistant_reply=raw,
        started_at=started_at,
    )
    return {"assistant_reply": raw}