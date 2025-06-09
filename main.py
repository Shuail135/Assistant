# main.py
from command import handle_command


def take_command():
    input_command = input("Command: ")
    return input_command


if __name__ == "__main__":
    while True:
        command = take_command()
        handle_command(command)
