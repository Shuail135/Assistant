from llama_cpp import Llama
import sys
from datetime import datetime

# Path to your GGUF model
MODEL_PATH = "LLM/glados-f16.Q4_K_M.gguf"

# Initialize the model
llm = Llama(model_path=MODEL_PATH, n_ctx=512, verbose=False)

print("GLaDOS Chatbot is ready. Ctrl+C to stop.\n")

try:
    while True:
        user_input = input("You: ").strip()
        now = datetime.now()
        current_time = now.strftime("%I:%M %p on %A")
        current_date = now.strftime("%A, %B %d, %Y")

        # Inject real time into system prompt
        SYSTEM_PROMPT = (
            "You are GLaDOS, a sarcastic and slightly dark AI assistant that sees users as test subjects. "
            f"Today's date is {current_date}. The current time is {current_time}. "
            "Respond in a witty, dry, and slightly unsettling tone. "
            "Keep responses in one to two sentences."
        )
        # Ensure the prompt ends just before assistant is expected to speak
        full_prompt = (
            f"<|system|>\n{SYSTEM_PROMPT}\n"
            f"<|user|>\n{user_input}\n"
            f"<|assistant|>\n"
        )

        # Generate response with tighter control
        output = llm(
            prompt=full_prompt,
            max_tokens=80,
            temperature=0.6, #0.7
            top_p=0.9,
            stop=["<|user|>", "<|system|>", "<|end|>", "</s>", "\n<|"],
            repeat_penalty=1.3
        )
        response = output["choices"][0]["text"]
        print(response)

        sys.stdout.flush()
        print()


except KeyboardInterrupt:
    print("\nExiting.")


