from datetime import datetime


def run():
    now = datetime.now()
    print("The current time is:", now.strftime("%I:%M %p"))
    return "The current time is:" + now.strftime("%I:%M %p")
