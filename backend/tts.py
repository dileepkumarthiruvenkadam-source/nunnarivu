import subprocess


def speak(text: str) -> None:
    """
    Use macOS 'say' command to speak the given text.
    """
    if not text:
        return
    subprocess.run(
        ["say", text],
        check=False
    )


if __name__ == "__main__":
    # Test: when you run `python backend/tts.py`
    # your Mac should speak this sentence.
    speak("Hello, I am Sunny, your local A I operating system.")