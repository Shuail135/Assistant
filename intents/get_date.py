from datetime import datetime

def run(request_input):
    print("Today is..." + datetime.now().strftime("%A, %B %d, %Y"))
    return "Today is..." + datetime.now().strftime("%A, %B %d, %Y")
