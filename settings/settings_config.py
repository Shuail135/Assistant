# settings_config.py
import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

_default_settings = {
    "theme": "light",
    "volume": 1.0,
    "music_provider": 0,
    "quit_command": "Quit",
    "file_import_path": "tts_models/custom_tts_model",
    "max_decoder_steps": 3000,
    "sampling_rate": 22050,
    "gate_threshold": 0.25,
    "hifigan_config_path": "hifi_gan/config_v1.json",
    "max_duration": 20,
    "stop_threshold": 0.9,
    "superres_strength": 10,
    "use_pronunciation": True,
    "similarity_threshold": 0.6
}

def get_settings():
    settings = _default_settings.copy()
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                settings.update(json.load(f))
        except Exception as e:
            print(f"Failed to read settings: {e}")
    return settings

def save_settings(new_settings: dict):
    with open(SETTINGS_PATH, "w") as f:
        json.dump(new_settings, f, indent=4)
