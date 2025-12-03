import os
import sys
import time

# Add project root to import backend modules
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.voice_listener import start_voice_listener
from backend.router import route_message, execute_action
from backend.tts import speak


def handle_voice_command(text):
    """
    Sends recognized command to Sunny and measures reaction time.
    """

    print(f"\n🎤 Command -> {text}")

    # start timer
    start_time = time.time()

    # Send to router
    result = route_message(text)

    action = result.get("action", "none")
    args = result.get("args", {})
    reply = result.get("assistant_reply", "")

    # run macOS action
    if action != "none":
        execute_action(action, args)

    # stop timer
    reaction_time = time.time() - start_time

    # speak and print Sunny's reply
    print(f"Sunny: {reply}")
    print(f"⏱ Reaction time: {reaction_time:.2f} seconds")
    speak(reply)


if __name__ == "__main__":
    print("🌞 Sunny Voice Assistant is running...")
    print("Say: 'Hey Sunny ...' to activate me.\n")

    start_voice_listener(handle_voice_command)