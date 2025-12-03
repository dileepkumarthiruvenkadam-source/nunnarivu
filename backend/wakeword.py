import sounddevice as sd
import numpy as np
from openwakeword import Model
import time


WAKEWORD = "hey sunny"   # your custom wake word


def start_wakeword_listener(on_detect):
    """
    Listens to the microphone and triggers on_detect()
    when it hears the custom wake word.
    """

    print("🎧 Wake word listener running...")
    print(f"Say your wake word: '{WAKEWORD}'")

    # load OpenWakeWord model
    model = Model()

    # audio settings
    samplerate = 16000
    blocksize = 512

    def audio_callback(indata, frames, time_info, status):
        if status:
            print("Audio error:", status)

        # convert audio to float32
        audio = indata[:, 0].astype(np.float32)

        # process through OpenWakeWord model
        scores = model.predict(audio)

        # check if wakeword detected
        if scores.get(WAKEWORD, 0) > 0.5:  # threshold
            print("🔥 Wake word detected!")
            on_detect()

    # start audio stream
    with sd.InputStream(
        channels=1,
        samplerate=samplerate,
        blocksize=blocksize,
        callback=audio_callback,
        dtype="float32"
    ):
        while True:
            time.sleep(0.1)


# Test mode
if __name__ == "__main__":
    def test_callback():
        print("Sunny says: Yes? I'm listening.")

    start_wakeword_listener(test_callback)