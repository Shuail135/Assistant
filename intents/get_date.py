from datetime import datetime

YELLOW = "\033[33m"
RESET = "\033[0m"

def run(request_input):
    print(f"{YELLOW}Today is {datetime.now().strftime('%A, %B %d, %Y')}{RESET}")
    return "Today is..." + datetime.now().strftime("%A, %B %d, %Y")
