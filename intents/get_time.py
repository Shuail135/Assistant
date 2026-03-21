from datetime import datetime

YELLOW = "\033[33m"
RESET = "\033[0m"

def run(request_input):
    now = datetime.now()
    print(f"{YELLOW}The current time is: {now.strftime('%I:%M %p')}{RESET}")
    if now.strftime("%p") == "AM":
        return "The current time is:" + now.strftime("%I:%M") + "Aeh Emm" # better pronunciation
    else:
        return "The current time is:" + now.strftime("%I:%M %p")
