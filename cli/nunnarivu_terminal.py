import os
import sys

# Add project root to sys.path so "backend" package can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.router import route_message, execute_action
from backend.tts import speak  # Sunny's voice


def main():
    print("☀️ Sunny (AI assistant) – type 'exit' to quit.\n")

    while True:
        try:
            user = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nSunny: Bye! 👋")
            speak("Bye! Talk to you later.")
            break

        if user.strip().lower() in {"exit", "quit"}:
            print("Sunny: Bye! 👋")
            speak("Bye! Talk to you later.")
            break

        # Ask router what to do
        result = route_message(user)

        action = result.get("action", "none")
        args = result.get("args", {})
        assistant_reply = result.get("assistant_reply", "")

        # Perform macOS action if needed
        if action != "none":
            execute_action(action, args)

        # Show and speak Sunny's reply
        print(f"\nSunny: {assistant_reply}\n")
        speak(assistant_reply)


if __name__ == "__main__":
    main()