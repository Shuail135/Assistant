# main.py
import threading
import queue
from command import handle_command

# thread safe queue
command_queue = queue.Queue()

def take_command():
    while True:
        input_command = input("Command: ")
        if input_command == "Quit":
            command_queue.put(None)
            break
        command_queue.put(input_command)


def command_worker():
    while True:
        command = command_queue.get()
        if command is None:
            break
        handle_command(command)
        command_queue.task_done()

if __name__ == "__main__":
    worker_thread = threading.Thread(target=command_worker)
    worker_thread.start()

    take_command()

    # Wait for all commands to be processed
    command_queue.join()
    worker_thread.join()