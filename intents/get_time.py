from datetime import datetime


def run(request_input):
    now = datetime.now()
    print("The current time is:", now.strftime("%I:%M %p"))
    if now.strftime("%p") == "AM":
        return "The current time is:" + now.strftime("%I:%M") + "Aeh Emm" # better pronunciation
    else:
        return "The current time is:" + now.strftime("%I:%M %p")
