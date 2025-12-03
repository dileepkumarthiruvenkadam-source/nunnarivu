import os
import sys

# Make sure we can import backend modules
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.llm_client import ask_llm
from backend.shell_actions import run_shell_command


SYSTEM_PROMPT = """
You are Sunny, an expert software engineer and coding assistant running locally on the user's Mac.
- You mainly help with Python, but you can also explain other languages.
- Prefer clear, simple solutions.
- When you show code, use concise examples.
- If the user mentions their project 'Nunnarivu', assume it is a Python/macOS project.
- You can provide full files, diffs, or explanations.
"""


def main():
    print("☀️ Sunny (coding assistant) – type 'exit' to quit.\n")

    # Conversation memory for better context
    history = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nSunny: Bye! 👋")
            break

        # Exit commands
        if user.strip().lower() in {"exit", "quit"}:
            print("Sunny: Bye! 👋")
            break

        # -------------------------------------------------------
        # NEW FEATURE — Execute Terminal Commands
        # -------------------------------------------------------
        if user.strip().lower().startswith("run:"):
            command = user.split("run:", 1)[1].strip()
            print(f"\n🔧 Running shell command: {command}\n")

            stdout, stderr, code = run_shell_command(command)

            print("📤 Output:")
            if stdout:
                print(stdout)

            if stderr:
                print("\n⚠️ Errors:")
                print(stderr)

            print(f"\nExit code: {code}\n")
            continue
        # -------------------------------------------------------

        # Normal LLM chat mode
        history.append({"role": "user", "content": user})

        reply = ask_llm(history)

        print("\nSunny:\n")
        print(reply)
        print()

        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()