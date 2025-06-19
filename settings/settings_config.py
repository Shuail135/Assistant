# settings_config.py
import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

_default_settings = {
    "theme": "light",
    "volume": 1.0,
    "music_provider": 0,
    "quit_command": "Quit",
    "file_import_path": "tts_models/GLaDOS-146",
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
