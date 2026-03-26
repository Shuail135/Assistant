import json
import queue
import sys
import re
from pathlib import Path

import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = Path("vosk_models/vosk-model-en-us-0.22-lgraph")
SAMPLE_RATE = 16000

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Vosk model not found at: {MODEL_PATH}\n"
        f"Download a model from https://alphacephei.com/vosk/models "
        f"and unzip it there."
    )

vosk_model = Model(str(MODEL_PATH))


def clean_stt_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()

    fillers = {"the", "uh", "um", "ah", "hmm", "mm"}
    words = text.split()

    while words and words[0] in fillers:
        words.pop(0)

    return " ".join(words)


def listen_for_command(
    prompt: str = "Speak now...",
    sample_rate: int = SAMPLE_RATE,
    device=None,
) -> str:
    print(prompt)

    audio_queue = queue.Queue()
    recognizer = KaldiRecognizer(vosk_model, sample_rate)

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)
        audio_queue.put(bytes(indata))

    try:
        with sd.RawInputStream(
            samplerate=sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
            device=device,
        ):
            while True:
                data = audio_queue.get()

                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    text = clean_stt_text(text)

                    if text:
                        print()
                        return text
                    else:
                        return ""

                else:
                    partial = json.loads(recognizer.PartialResult()).get("partial", "").strip()
                    partial = clean_stt_text(partial)

                    if partial:
                        print(f"\rListening: {partial}", end="", flush=True)

    except Exception as e:
        print(f"\nVoice input error: {e}")
        return ""