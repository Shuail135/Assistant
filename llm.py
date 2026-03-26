from llama_cpp import Llama

MODEL_PATH = "./LLM/glados-qwen25-05b-f32.gguf"

SYSTEM_PROMPT = (
    "You are a dry, intelligent assistant with a GLaDOS-like tone. "
    "Be concise, sharp, slightly sarcastic, and emotionally detached."
    "You must respond in strictly fluent English. Never use Chinese or mixed-language words."
)

# Internal singleton instance
_llm = None


def _build_prompt(user_input: str) -> str:
    return f"""<|system|>
{SYSTEM_PROMPT}
<|user|>
{user_input}
<|assistant|>
"""


def load_model():
    print("[llm.py]Loading LLM...")
    global _llm
    if _llm is None:
        _llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=8,
            n_batch=256,
            verbose=False
        )
    return _llm


def generate(user_input: str,
             max_tokens: int = 100,
             temperature: float = 0.75,
             top_p: float = 0.9,
             repeat_penalty: float = 1.15) -> str:
    llm = load_model()
    prompt = _build_prompt(user_input)

    output = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        repeat_penalty=repeat_penalty,
        stop=["<|user|>", "<|assistant|>"]
    )

    return output["choices"][0]["text"].strip()