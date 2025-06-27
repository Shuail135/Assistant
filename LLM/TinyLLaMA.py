from llama_cpp import Llama
import time

MODEL_PATH = "glados-f16.Q4_K_M.gguf"
MAX_TOKENS = 256
MAX_CONTEXT_LENGTH = 2048

SYSTEM_PROMPT = (
    "You are GLaDOS, an artificial intelligence known for your sarcastic, dark, and unsettling personality. "
    "You see the user as a human test subject in an endless experiment. "
    "Respond with dry wit, short sentences, and a sharp edge. End each response with '<|end|>'."
)

llm = Llama(model_path=MODEL_PATH, n_ctx=MAX_CONTEXT_LENGTH)

print("TinyLLaMA (stateless GLaDOS chatbot) is ready! Ctrl+C to exit.\n")

try:
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        prompt = f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{user_input}\n<|assistant|>\n"
        response_text = ""

        for chunk in llm(prompt, max_tokens=MAX_TOKENS, stop=["<|user|>", "<|system|>", "<|end|>"], stream=True):
            token = chunk["choices"][0]["text"]
            response_text += token
            print(token, end="", flush=True)
            time.sleep(0.01)

        print("\n")

except KeyboardInterrupt:
    print("\n👋 Exiting.")
