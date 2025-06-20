# main.py
# Runs in threads so that it can handle and take command at the same time. handle_command will haul when
# requires input in take_command

import os
import threading
import queue
import sys
from command import handle_command
from tts_controller import speak
from settings.settings_config import get_settings

# thread safe queue
command_queue = queue.Queue()
input_request_queue = queue.Queue()
input_response_queue = queue.Queue()

def request_input(prompt):
    input_request_queue.put(prompt)
    speak(prompt)
    response = input_response_queue.get()
    return response

def take_command():
    while True:
        # Prioritize input requests -> Avoid race condition
        try:
            request = input_request_queue.get(timeout=1) # if still have aka ur pc slow aka increase timeout
            user_input = input(request)
            input_response_queue.put(user_input)
            input_request_queue.task_done()
            #continue
        except queue.Empty:
            pass

        input_command = input("Command: ")
        quit_command = get_settings()["quit_command"]
        if input_command == quit_command:
            print("Quiting...")
            command_queue.put(None)
            sys.exit()
        command_queue.put(input_command)


def command_worker():
    while True:
        command = command_queue.get()
        if command is None:
            break
        similarity_threshold=get_settings()["similarity_threshold"]
        handle_command(command, request_input, similarity_threshold)
        command_queue.task_done()

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

_default_settings = {
    "theme": "light",
    "volume": 1.0,
    "music_provider": 0,
    "quit_command": "Quit",
    "file_import_path": "tts_models/GLaDOS-146",
    "similarity_threshold": 0.6
}


if __name__ == "__main__":

    worker_thread = threading.Thread(target=command_worker)
    worker_thread.start()

    take_command()
    # Wait for all commands to be processed
    command_queue.join()
    worker_thread.join()
