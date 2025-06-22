
# Custom Voice Assistant (CPU-Only)

A simple customizable **CPU-Only Voice Assistant** that allows you to integrate your own Tacotron 2 model for Text-to-Speech (TTS) synthesis.  
This assistant captures user input, processes commands, and generates voice responses using your custom voice model locally.

The project is designed to work entirely on CPU — no GPU is required.

---

## ⚙️ Project Setup & Usage

This section includes both full setup instructions and usage guide.

### 1️⃣ Clone Repository

Clone your repository (or prepare your local project folder).

### 2️⃣ Install Required Packages

The project dependencies are listed in `requirements.txt`. Install them using:

```bash
pip install -r requirements.txt
```

✅ Make sure you are using Python 3.9+.(Tested environment: Python 3.10)

Since this project is CPU-only, no CUDA or GPU configuration is necessary.

### 3️⃣ Prepare Custom Tacotron 2 Model

- Train or download a pre-trained Tacotron 2 model (e.g. [Model from Hugging Face][hugging_face]).
- Place your Tacotron 2 checkpoint file inside the `tts_model/` directory. (Recommend)

[hugging_face]: https://huggingface.co/models?sort=trending&search=tacotron2

### 4️⃣ Update Tacotron 2 Model Path

- Run `settings.py`.
```bash
python settings.py
```

- Update the TTS model path to your Tacotron 2 model
- Adjust other settings if needed

### 5️⃣ Run the Voice Assistant

Finally, start your assistant by running:

```bash
python main.py
```

The assistant will start taking voice/text commands and respond using your custom voice model.

---

## 🔧 Notes

- ✅ Fully CPU compatible (but slower inference compared to GPU).
- ✅ No CUDA or GPU drivers required.
- ✅ Everything operates locally.
- ✅ The model will try to understand your intent through your human text, and find the most suitable intent for you.
- ⚠️ This README assumes you already have a trained Tacotron 2 model; trained model is not included.

---

## Current Development

- Convert human text to corresponding intents command ✅
  - Cached sentence embeddings + cosine similarity with auto-invalidation when intents file is changed ✅
- Different Intents are still in progress, lacking in functionality.
  - Current intents:
    - Play Music
    - Tell Time
    - Tell Date
    - Calculator(Can calculate from english math)
    - Open Settings
    - Reload Model (after modified TTS settings, reload model to apply changes)
- With GUI real time settings ✅
- Will build a local speech to text(or even your only voice recognization lets see)
- Building Gernative AI (TinyLLaMA (1.1B) with llama.cpp + Prompt Engineering or LoRA)
