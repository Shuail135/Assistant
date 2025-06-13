# Cached sentence embeddings + cosine similarity with auto-invalidation when csv file changed
# Used to handle command

import os
import numpy as np
import pandas as pd
import pickle
import importlib.util
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from tts_controller import speak

# File paths
CSV_FILE = "intents.csv"
EMBEDDINGS_FILE = "intent_embeddings.npy"
LABELS_FILE = "intent_labels.pkl"
INTENT_FOLDER = "intents"

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Build embedding cache
def compute_and_cache_embeddings():
    print("[command.py]: Recomputing embeddings...")
    df = pd.read_csv(CSV_FILE)
    texts = df["text"].tolist()
    labels = df["intent"].tolist()

    embeddings = embedder.encode(texts)
    np.save(EMBEDDINGS_FILE, embeddings)
    with open(LABELS_FILE, "wb") as f:
        pickle.dump(labels, f)

    return embeddings, labels

# Check if cache needs update
def should_recompute():
    return (
        not os.path.exists(EMBEDDINGS_FILE)
        or not os.path.exists(LABELS_FILE)
        or os.path.getmtime(CSV_FILE) > os.path.getmtime(EMBEDDINGS_FILE)
    )

# Load or compute embeddings
if should_recompute():
    intent_embeddings, intent_labels = compute_and_cache_embeddings()
else:
    intent_embeddings = np.load(EMBEDDINGS_FILE)
    with open(LABELS_FILE, "rb") as f:
        intent_labels = pickle.load(f)
    print("[command.py]: Loaded cached embeddings.")

# Intent file loader
def run_intent_action(intent_name, request_input):
    intent_file = os.path.join(INTENT_FOLDER, f"{intent_name}.py")

    if not os.path.isfile(intent_file):
        print(f"[command.py]: Intent '{intent_name}' known but file not found.")
        return

    try:
        spec = importlib.util.spec_from_file_location("intent_module", intent_file)
        intent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(intent_module)

        if hasattr(intent_module, "run"):
            speak(intent_module.run(request_input))
        else:
            print(f"[command.py]: '{intent_name}.py' found, but no run() defined.")
    except Exception as e:
        print(f"[command.py]: Failed to run intent '{intent_name}': {e}")

# Main intent matcher
def handle_command(text, request_input, similarity_threshold=0.6):
    user_vec = embedder.encode(text)
    similarities = cosine_similarity([user_vec], intent_embeddings)[0]

    max_index = np.argmax(similarities)
    max_score = similarities[max_index]
    best_intent = intent_labels[max_index]

    print(f"[command.py]: Best match: {best_intent} (score: {max_score:.3f})")

    if max_score < similarity_threshold:
        speak("I’m not sure what you mean.")
        return

    run_intent_action(best_intent, request_input)
