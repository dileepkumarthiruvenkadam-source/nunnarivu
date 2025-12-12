"""
backend/nunnarivu_local.py

This is the "Nunnarivu Local" module – the local brain that runs on your Mac.
It talks to the LLM (currently hosted on the server via llm_client.ask_llm)
and gives you a clean API to use in other parts of the project.
"""

from __future__ import annotations

from typing import List, Dict, Optional

# Support both "python -m backend.nunnarivu_local" and "python backend/nunnarivu_local.py"
try:
    from .llm_client import ask_llm
except ImportError:  # direct script run fallback
    from llm_client import ask_llm


SYSTEM_PROMPT_LOCAL = (
    "You are Nunnarivu Local – the local brain running on the user's Mac.\n"
    "- Your name when speaking is Sunny.\n"
    "- You control and coordinate tasks on macOS via higher-level tools.\n"
    "- You DO NOT describe low-level model details; focus on helping the user.\n"
    "- You are part of an offline-first AI OS layer called Nunnarivu.\n"
    "- When unsure, ask a short clarification question instead of guessing.\n"
    "- Be concise, friendly, and practical.\n"
)


def nunnarivu_local_chat(
    user_text: str,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    High-level chat entry point for Nunnarivu Local.

    Parameters
    ----------
    user_text : str
        The latest user message.
    history : Optional[List[Dict[str, str]]]
        Optional previous messages in the ChatML-like format:
        [{"role": "user"|"assistant"|"system", "content": "..."}]

    Returns
    -------
    str
        Sunny's reply as plain text.
    """

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT_LOCAL}
    ]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": user_text})

    reply = ask_llm(messages)
    return reply


def build_history_pair(user_text: str, assistant_text: str) -> List[Dict[str, str]]:
    """
    Convenience helper: build a minimal history list from one exchange.

    Example:
        hist = build_history_pair("open safari", "Opening Safari now.")
        next_reply = nunnarivu_local_chat("and open downloads", history=hist)
    """
    return [
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ]


if __name__ == "__main__":
    # Simple CLI test for Nunnarivu Local.
    # You can run:
    #   python backend/nunnarivu_local.py
    # or:
    #   python -m backend.nunnarivu_local

    import sys

    if len(sys.argv) > 1:
        # Single-shot mode: python backend/nunnarivu_local.py "your question"
        user_msg = " ".join(sys.argv[1:])
        print("🔹 Nunnarivu Local (single-shot)")
        print(f"You: {user_msg}")
        reply = nunnarivu_local_chat(user_msg)
        print("Sunny:", reply)
    else:
        # Interactive mode
        print("🧠 Nunnarivu Local – Sunny chat mode")
        print("Type 'exit' to quit.\n")

        history: List[Dict[str, str]] = []

        while True:
            try:
                user_msg = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye from Nunnarivu Local.")
                break

            if user_msg.lower() in {"exit", "quit"}:
                print("Goodbye from Nunnarivu Local.")
                break

            reply = nunnarivu_local_chat(user_msg, history=history)
            print(f"Sunny: {reply}\n")

            # Extend history so the model keeps short context
            history.extend(
                [
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": reply},
                ]
            )