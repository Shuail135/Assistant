from llama_cpp import Llama

MODEL_PATH = "./LLM/glados-qwen25-05b-f16.gguf"

SYSTEM_PROMPT = (
    "You are a dry, intelligent assistant with a GLaDOS-like tone. "
    "Be concise, sharp, slightly sarcastic, and emotionally detached."
)

def build_prompt(user_input: str):
    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
{user_input}
<|assistant|>
"""

print("Loading model...")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,     # adjust based on your CPU
    n_batch=256,
)

print("GLaDOS ready. Type 'exit' to quit.\n")

while True:
    user = input("You: ").strip()
    if user.lower() in {"exit", "quit"}:
        break

    prompt = build_prompt(user)

    output = llm(
        prompt,
        max_tokens=100,
        temperature=0.85,
        top_p=0.9,
        repeat_penalty=1.15,
        stop=["<|user|>", "<|assistant|>"]
    )

    response = output["choices"][0]["text"].strip()
    print(f"\nGLaDOS: {response}\n")