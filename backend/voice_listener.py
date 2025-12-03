import json
import queue
import time
import sounddevice as sd
from vosk import Model, KaldiRecognizer


WAKE_PHRASE = "hey sunny"


def start_voice_listener(on_command):
    """
    Voice listener with:
      - Wake phrase: "hey sunny"
      - Conversation mode: after wake, every final phrase -> on_command()
      - Echo protection: ignores commands that come too soon after the last one
      - Special rule: any command containing 'volume' is treated as one-shot:
        after handling it, we go back to idle mode to avoid loops.
    """

    print("🎧 Voice listener running...")
    print("Say: 'Hey Sunny ...' (example: 'Hey Sunny open safari')")

    # Load offline speech model (small, fast)
    model = Model("models/vosk-model-small-en-us-0.15")

    # Limited grammar for better accuracy
    grammar = [
        "hey", "sunny",
        "open", "close",
        "safari", "chrome", "notes", "music", "downloads", "documents",
        "volume", "to",
        "zero", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "twenty", "thirty", "forty", "fifty",
        "sixty", "seventy", "eighty", "ninety", "hundred",
        "what", "can", "you", "do",
        "stop", "listening", "sleep", "go", "thanks", "thank", "bye"
    ]

    recognizer = KaldiRecognizer(model, 16000, json.dumps(grammar))
    recognizer.SetWords(True)

    audio_queue = queue.Queue()
    state = {
        "mode": "idle",               # idle | waiting_for_command | conversation
        "last_command_time": 0.0,
    }

    def audio_callback(indata, frames, time_info, status):
        if status:
            print("Audio error:", status)
        audio_queue.put(bytes(indata))

    def maybe_send_command(command_text: str):
        """
        Send a command to on_command, with echo loop protection:
        - ignore ANY command that comes <1.5s after the previous one
        - if 'volume' in the command, treat it as one-shot:
          go back to idle right after sending it
        """
        now = time.time()
        last_time = state["last_command_time"]

        # global echo suppression
        if (now - last_time) < 1.5:
            print(f"🔁 Ignoring command too soon after previous one (likely echo): {command_text}")
            return

        state["last_command_time"] = now

        print(f"🎤 Command -> {command_text}")
        on_command(command_text)

        # If this is a volume command, treat as one-shot:
        # go back to idle so Sunny's own TTS doesn't trigger more volume commands.
        if "volume" in command_text:
            print("🔇 One-shot volume command handled, returning to idle mode.")
            state["mode"] = "idle"

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=audio_callback
    ):
        while True:
            data = audio_queue.get()

            is_final = recognizer.AcceptWaveform(data)
            if is_final:
                result = recognizer.Result()
            else:
                result = recognizer.PartialResult()

            try:
                text = json.loads(result).get("text", "").lower().strip()
            except Exception:
                continue

            if not text:
                continue

            print("Heard:", text)

            # Only act on FINAL phrases
            if not is_final:
                continue

            # Conversation stop phrases
            if any(
                phrase in text
                for phrase in [
                    "stop listening",
                    "go to sleep",
                    "bye sunny",
                    "bye",
                    "thank you",
                ]
            ):
                print("🛌 Conversation ended, going back to idle mode.")
                state["mode"] = "idle"
                continue

            # After wake, waiting for first command
            if state["mode"] == "waiting_for_command":
                print(f"🔥 Wake phrase previously detected. Command: {text}")
                state["mode"] = "conversation"
                maybe_send_command(text)
                continue

            # In conversation mode: every final phrase is a command/message
            if state["mode"] == "conversation":
                if text.startswith(WAKE_PHRASE):
                    command = text[len(WAKE_PHRASE):].strip() or None
                    if command:
                        print(f"🔥 Wake phrase inside conversation. Command: {command}")
                        maybe_send_command(command)
                    else:
                        print("👉 Wake phrase repeated, still in conversation mode.")
                else:
                    print(f"🗣 Conversation command: {text}")
                    maybe_send_command(text)
                continue

            # IDLE MODE: look for wake phrase
            if state["mode"] == "idle":
                if text.startswith(WAKE_PHRASE):
                    command = text[len(WAKE_PHRASE):].strip()
                    if command == "":
                        print("👉 Wake phrase detected. Waiting for first command...")
                        state["mode"] = "waiting_for_command"
                    else:
                        print(f"🔥 Wake phrase detected! Command: {command}")
                        state["mode"] = "conversation"
                        maybe_send_command(command)