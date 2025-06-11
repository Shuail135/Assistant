
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

- Train or download a pre-trained Tacotron 2 model (ensure it's compatible with your current TTS pipeline).
- Place your Tacotron 2 checkpoint file inside the `tts_model/` directory.

Example:

```bash
tts_model/custom_tacotron2_checkpoint.pth
```

### 4️⃣ Update Tacotron 2 Model Path

- Open `tts_controller.py`.
- Locate the variable where the Tacotron 2 model path is specified.
- Modify the path to point to your custom model.

Example:

```python
tacotron_path = 'tts_model/custom_tacotron2_checkpoint.pth' #change the voice model path here
```

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
- ✅ The model will try to understand your intent through your text, and find the most suitable intent for you.
- ⚠️ Tacotron 2 models can still consume significant CPU and RAM resources. (I did try to reduce usage... A LOT...)
- ⚠️ This guide assumes you already have a trained Tacotron 2 model; trained model is not included.

---

## Current Development

- Still in progress, lacking in functionality.
- Will build a local speech to text(or even your only voice recognization lets see)
