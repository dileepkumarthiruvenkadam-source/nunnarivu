import sys
import time
from backend.router import route_message
# from backend.router import execute_action   # ❌ old import (commented, not deleted)

def main():
    print("🟢 Nunnarivu Terminal — Sunny Ready")
    print("Type your message. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "exit":
            print("Goodbye!")
            sys.exit(0)

        # Route the text to the router (LLM + action detection)
            # Measure reaction time
        start_time = time.time()
        sunny_reply = route_message(user_input)
        end_time = time.time()
        reaction = end_time - start_time


        # If router was returning an action dict earlier, we used:
        # execute_action(action)
        # Removed but NOT deleted
        #
        # Example of old logic:
        # action = route_message(user_input)
        # if action:
        #     execute_action(action)

        if isinstance(sunny_reply, dict):
            text = sunny_reply.get("assistant_reply", str(sunny_reply))
        else:
            text = str(sunny_reply)

        print(f"Sunny: {text}")
        print(f"⏱ Reaction time: {reaction:.2f} seconds")

if __name__ == "__main__":
    main()