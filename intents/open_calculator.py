import re
from number_parser import parse

def run(request_input):
    math_in_english = request_input("Tell me the expression: ")
    expression = convert_english_math_to_expression(math_in_english)
    print(f"Calculating '{expression}'")
    result = safe_evaluate(expression)
    print("Result:", result)
    return f"The result is... '{result}.'"


def convert_english_math_to_expression(text):
    text = text.lower()
    text = text.replace('-', ' ')
    text = text.replace(' and ', ' ')

    # First parse entire sentence into numerals
    parsed_text = parse(text)

    # Now replace operators after numbers are parsed
    replacements = {
        "plus": "+",
        "minus": "-",
        "times": "*",
        "time": "*",
        "multiplied by": "*",
        "divided by": "/",
        "over": "/"
    }

    for word, symbol in replacements.items():
        parsed_text = parsed_text.replace(word, f" {symbol} ")

    parsed_text = re.sub(r'\s+', ' ', parsed_text).strip()

    return parsed_text

# Now add safe evaluation function:
def safe_evaluate(expression):
    try:
        result = eval(expression)
        return result
    except:
        return "not calculated"

# Test case
if __name__ == "__main__":
    def dummy_request_input(prompt):
        return "Thirty four times two"

    run(dummy_request_input)