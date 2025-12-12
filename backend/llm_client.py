import requests
from typing import List, Dict

# Talk to the server-side Ollama instance
OLLAMA_URL = "http://10.2.51.11:11434/api/generate"
MODEL_NAME = "phi3:latest"


def _messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Convert a chat-style messages list into a single prompt string
    suitable for /api/generate.
    """
    parts = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")

        if role == "system":
            parts.append(f"[System]\n{content}\n")
        elif role == "assistant":
            parts.append(f"[Assistant]\n{content}\n")
        else:  # user or other
            parts.append(f"[User]\n{content}\n")

    # Encourage the model to respond as assistant
    parts.append("[Assistant]\n")
    return "\n".join(parts)


def ask_llm(messages: List[Dict[str, str]]) -> str:
    """
    Talk to the server-side Ollama model (phi3) using /api/generate.
    """
    prompt = _messages_to_prompt(messages)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    # For non-streaming, Ollama returns a single JSON object with "response"
    return data.get("response", "").strip()


if __name__ == "__main__":
    # Simple manual test when you run:
    #   python backend/llm_client.py
    test_messages = [
        {"role": "system", "content": "You are Sunny, an AI OS for macOS."},
        {"role": "user", "content": "Hello, who are you?"},
    ]
    reply = ask_llm(test_messages)
    print("Model replied:")
    print(reply)
