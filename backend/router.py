from typing import Dict, Any, Optional
from backend.llm_client import ask_llm
from backend.mac_actions import (
    open_app,
    close_app,
    open_url,
    open_folder,
    set_volume,
)
import json
import re


# ---------------------------------------------------------
# FAST RULE-BASED ROUTER (no LLM)
# ---------------------------------------------------------
def _rule_based_route(user_msg: str) -> Optional[Dict[str, Any]]:
    """
    Very fast parser for common commands.
    If it understands the command, returns a route dict.
    Otherwise returns None → fallback to LLM router.
    """
    text = user_msg.lower().strip()

    # open safari / open chrome / open notes etc.
    if text.startswith("open "):
        rest = text[5:].strip()

        # special cases for websites
        if "youtube" in rest:
            url = "https://www.youtube.com"
            return {
                "action": "open_url",
                "args": {"url": url},
                "assistant_reply": "Opening YouTube.",
            }
        if "google" in rest:
            url = "https://www.google.com"
            return {
                "action": "open_url",
                "args": {"url": url},
                "assistant_reply": "Opening Google.",
            }

        # treat as app name
        app_name = rest.title()  # "safari" -> "Safari"
        return {
            "action": "open_app",
            "args": {"name": app_name},
            "assistant_reply": f"Opening {app_name} now.",
        }

    # close safari / close chrome
    if text.startswith("close "):
        rest = text[6:].strip()
        app_name = rest.title()
        return {
            "action": "close_app",
            "args": {"name": app_name},
            "assistant_reply": f"Closing {app_name}.",
        }

    # volume commands: "set volume to 20", "volume 10", "volume twenty" etc.
    if "volume" in text:
        number_words = {
            "zero": 0,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
            "twenty": 20,
            "thirty": 30,
            "forty": 40,
            "fifty": 50,
            "sixty": 60,
            "seventy": 70,
            "eighty": 80,
            "ninety": 90,
            "hundred": 100,
        }

        tokens = text.split()
        nums = []

        # collect both digit numbers and word numbers
        for t in tokens:
            if t.isdigit():
                nums.append(int(t))
            elif t in number_words:
                nums.append(number_words[t])

        if nums:
            # take the last mentioned number as the target volume
            level = nums[-1]
            level = max(0, min(level, 100))
            return {
                "action": "set_volume",
                "args": {"level": level},
                "assistant_reply": f"Setting volume to {level}.",
            }
        else:
            return {
                "action": "none",
                "args": {},
                "assistant_reply": "Please tell me a volume level between 0 and 100.",
            }

    # open downloads / open documents
    if "open downloads" in text:
        # you can hardcode your own path later
        return {
            "action": "open_folder",
            "args": {"path": "/Users/dileepthiruvenkadam/Downloads"},
            "assistant_reply": "Opening Downloads folder.",
        }

    if "open documents" in text:
        return {
            "action": "open_folder",
            "args": {"path": "/Users/dileepthiruvenkadam/Documents"},
            "assistant_reply": "Opening Documents folder.",
        }

    # No fast rule matched → use LLM
    return None


# ---------------------------------------------------------
# LLM-BASED ROUTER (fallback for complex commands)
# ---------------------------------------------------------
ROUTER_PROMPT = """
You are Sunny, the AI assistant of Nunnarivu, acting as a very fast action router.

Given ONE user message, decide if a macOS action is required and return ONLY a single JSON object.

Valid actions:
- "open_app"      → open an app.          args: {"name": "<AppName>"}
- "close_app"     → close an app.         args: {"name": "<AppName>"}
- "open_url"      → open a website.       args: {"url": "<https URL>"}
- "open_folder"   → open a folder.        args: {"path": "<POSIX path>"}
- "set_volume"    → volume 0–100.         args: {"level": <int>}
- "none"          → no action.            args: {}

Output format (MUST be exact):
{
  "action": "open_app" | "close_app" | "open_url" | "open_folder" | "set_volume" | "none",
  "args": {...},
  "assistant_reply": "short sentence for user"
}

Rules:
- Be extremely fast and concise.
- NO markdown, NO code fences.
- Output ONLY the JSON object.
"""


def _extract_first_valid_json(raw: str) -> str:
    """
    Attempts to extract the first valid JSON object from raw text.
    Removes any accidental code fences.
    """
    text = raw.strip()

    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()

    opens = [i for i, c in enumerate(text) if c == "{"]
    closes = [i for i, c in enumerate(text) if c == "}"]

    for start in opens:
        for end in closes:
            if end > start:
                candidate = text[start:end + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue

    return text


def _llm_route(user_msg: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    raw = ask_llm(messages)
    cleaned = _extract_first_valid_json(raw)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "action": "none",
            "args": {},
            "assistant_reply": raw,
        }

    return {
        "action": data.get("action", "none"),
        "args": data.get("args", {}),
        "assistant_reply": data.get("assistant_reply", ""),
    }


# ---------------------------------------------------------
# PUBLIC ROUTER: tries rules first, then LLM
# ---------------------------------------------------------
def route_message(user_msg: str) -> Dict[str, Any]:
    # 1) try fast rule-based routing
    fast = _rule_based_route(user_msg)
    if fast is not None:
        return fast

    # 2) fallback to LLM for complex/unknown commands
    return _llm_route(user_msg)


# ---------------------------------------------------------
# Execute macOS actions
# ---------------------------------------------------------
def execute_action(action: str, args: Dict[str, Any]) -> None:
    if action == "open_app":
        open_app(args.get("name", ""))
    elif action == "close_app":
        close_app(args.get("name", ""))
    elif action == "open_url":
        open_url(args.get("url", ""))
    elif action == "open_folder":
        open_folder(args.get("path", ""))
    elif action == "set_volume":
        try:
            level = int(args.get("level", 50))
        except Exception:
            level = 50
        set_volume(level)
    # "none" → do nothing


if __name__ == "__main__":
    print(route_message("open safari"))
    print(route_message("close safari"))
    print(route_message("set volume to 10"))