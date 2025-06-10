# Cached sentence embeddings + cosine similarity with auto-invalidation when csv file changed
# Used to handle command

import os
import numpy as np
import pandas as pd #pip install pandas
import pickle
import importlib.util
from sentence_transformers import SentenceTransformer # pip install sentence-transformers
from sklearn.metrics.pairwise import cosine_similarity

from tts_controller import speak

# File paths
CSV_FILE = "intents.csv"
EMBEDDINGS_FILE = "intents/intent_embeddings.npy"
LABELS_FILE = "intents/intent_labels.pkl"
INTENT_FOLDER = "intents"

# Load sentence embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def compute_and_cache_embeddings():
    print("[command.py]:Recomputing embeddings from CSV...")
    df = pd.read_csv(CSV_FILE)
    texts = df["text"].tolist()
    labels = df["intent"].tolist()

    embeddings = embedder.encode(texts)
    np.save(EMBEDDINGS_FILE, embeddings)

    with open(LABELS_FILE, "wb") as f:
        pickle.dump(labels, f)

    return embeddings, labels

# Should recompute if intents.csv file has been changed
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
    print("[command.py]:Loaded cached embeddings.")

def run_intent_action(intent_name):
    intent_file = os.path.join(INTENT_FOLDER, f"{intent_name}.py")

    # Error handler if can't run intent
    if not os.path.isfile(intent_file):
        print(f"[command.py]: The intent '{intent_name}' known, but no matching file was found.")
        return

    try:
        spec = importlib.util.spec_from_file_location("intent_module", intent_file)
        intent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(intent_module)

        if hasattr(intent_module, "run"):
            speak(intent_module.run())
        else:
            print(f"[command.py]: '{intent_name}.py' found, but no run() function is defined.")
    except Exception as e:
        print(f"[command.py]: Failed to run intent '{intent_name}': {e}")

# Main intent handler
def handle_command(text, similarity_threshold=0.6):
    user_vec = embedder.encode(text)
    similarities = cosine_similarity([user_vec], intent_embeddings)[0]

    max_index = np.argmax(similarities)
    max_score = similarities[max_index]
    best_intent = intent_labels[max_index]

    print(f"[command.py]:Best match: {best_intent} (score: {max_score:.3f})")

    if max_score < similarity_threshold:
        speak("I’m not sure what you mean.")
        return

    run_intent_action(best_intent)
