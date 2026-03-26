# main.py
# Runs in threads so that it can handle and take command at the same time.
# handle_command will halt when it requires input in take_command

import threading
import queue
import time
import re

from command import handle_command
from tts_controller import speak
from settings.settings_config import get_settings
from audio_state import tts_playing, assistant_busy
from speech_to_text import listen_for_command

# thread-safe queues
command_queue = queue.Queue()
input_request_queue = queue.Queue()
input_response_queue = queue.Queue()

def clean_stt_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()

    fillers = {"the", "uh", "um", "ah", "hmm", "mm", "okay", "ok"}
    words = text.split()

    # remove leading fillers repeatedly
    while words and words[0] in fillers:
        words.pop(0)

    # if only fillers were present
    if not words:
        return ""

    return " ".join(words)

def request_input(prompt):
    speak(prompt)

    while tts_playing.is_set():
        time.sleep(0.05)

    print("[INPUT] Waiting for spoken response...")
    response = listen_for_command("Listening for response...")

    if not response:
        print("[INPUT] No spoken response detected.")
        return ""

    response = clean_stt_text(response)

    print(f"[INPUT] Heard response: {response}")
    return response


def wait_for_tts_and_cooldown(cooldown=0.7):
    while tts_playing.is_set():
        time.sleep(0.05)
    time.sleep(cooldown)


def take_command():
    while True:
        try:
            request = input_request_queue.get(timeout=0.2)
            user_input = input(f"\n{request}\n> ")
            input_response_queue.put(user_input)
            input_request_queue.task_done()
        except queue.Empty:
            pass

        while assistant_busy.is_set() or tts_playing.is_set():
            time.sleep(0.05)

        input_command = listen_for_command()

        if not input_command:
            print("\nNo speech detected. Try again.")
            continue

        quit_command = get_settings()["quit_command"].lower().strip()

        if input_command.lower().strip() == quit_command:
            print("Quitting...")
            command_queue.put(None)
            break

        input_command = clean_stt_text(input_command)

        if not input_command:
            print("\nIgnored.")
            continue

        command_queue.put(input_command)


def command_worker():
    while True:
        command = command_queue.get()
        if command is None:
            command_queue.task_done()
            break

        assistant_busy.set()
        try:
            similarity_threshold = get_settings()["similarity_threshold"]
            handle_command(command, request_input, similarity_threshold)
        finally:
            assistant_busy.clear()
            command_queue.task_done()


if __name__ == "__main__":
    worker_thread = threading.Thread(target=command_worker, daemon=True)
    worker_thread.start()

    take_command()

    command_queue.join()
    worker_thread.join()