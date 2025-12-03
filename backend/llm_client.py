import requests
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3:mini"

def ask_llm(messages: List[Dict[str, str]]) -> str:
    """
    Talk to the local Ollama model (phi3).

    messages example:
    [
        {"role": "system", "content": "You are Sunny, an AI OS for macOS."},
        {"role": "user", "content": "Hello!"}
    ]
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]


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
