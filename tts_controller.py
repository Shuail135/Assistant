# tts_controller.py
# Voice model controller

import numpy as np
import torch
import json
import resampy
import scipy.signal
import sounddevice as sd

from hifi_gan.env import AttrDict
from hifi_gan.models import Generator
from hifi_gan.denoiser import Denoiser
from hifi_gan.meldataset import mel_spectrogram, MAX_WAV_VALUE

from TTS_TT2.hparams import create_hparams
from TTS_TT2.model import Tacotron2
from TTS_TT2.text import text_to_sequence

from settings.settings_config import get_settings

tacotron2 = None
hparams = None
hifigan = None
h = None
denoiser = None
tacotron2_path = get_settings()["file_import_path"]
hifigan_path = get_settings()["hifigan_path"]
superres_path = "tts_models/Superres_Twilight_33000"
hifigan_config = get_settings()["hifigan_config_path"]
superres_config = "hifi_gan/config_32k.json"
CMU_DICT_PATH = "cmudict/merged.dict.txt"
denoiser_strength = get_settings()["denoiser_strength"]


def load_hifigan(model_path, config_path):
    with open(config_path) as f:
        config = json.load(f)
    h = AttrDict(config)
    model = Generator(h).to("cpu")
    checkpoint = torch.load(model_path, map_location="cpu")
    model.load_state_dict(checkpoint["generator"])
    model.eval()
    model.remove_weight_norm()
    denoiser = Denoiser(model, mode="normal")
    return model, h, denoiser

def load_tacotron2(model_path):
    hparams = create_hparams()
    hparams.sampling_rate = get_settings()["sampling_rate"]
    hparams.max_decoder_steps = get_settings()["max_decoder_steps"]
    hparams.gate_threshold = 0.25
    model = Tacotron2(hparams)
    checkpoint = torch.load(model_path, map_location="cpu")
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, hparams

def load_TTS(tts_path, hifigan_path, hifigan_config_path, superres_path, superres_config):
    global tacotron2, hparams, hifigan, h, denoiser, hifigan_sr, h2, denoiser_sr
    tacotron2, hparams = load_tacotron2(tts_path)
    hifigan, h, denoiser = load_hifigan(hifigan_path, hifigan_config_path)
    hifigan_sr, h2, denoiser_sr = load_hifigan(superres_path, superres_config)

print("[TTS] Loading models...")
try:
    load_TTS(tacotron2_path, hifigan_path, hifigan_config, superres_path, superres_config)
except:
    from kivy.app import App

    settings_screen = App.get_running_app().settings_screen
    (tts_path, max_decoder_steps, sample_rate, stop_threshold, hifigan_config_path, max_duration,
     superres_strength, use_pronunciation, hifigan_path, denoiser_strength) = settings_screen.get_TTS_value()
    load_TTS(tts_path, hifigan_path, hifigan_config_path, superres_path, superres_config)

print("[TTS] Models loaded.")


def test_model():
    global tacotron2, hparams, hifigan, h, denoiser, hifigan_sr, h2, denoiser_sr

    from kivy.app import App
    settings_screen = App.get_running_app().settings_screen
    (tts_path, max_decoder_steps, sample_rate, stop_threshold, hifigan_config_path, max_duration,
     superres_strength, use_pronunciation, hifigan_path, denoiser_strength) = settings_screen.get_TTS_value()

    load_TTS(tts_path, hifigan_path, hifigan_config_path, superres_path, superres_config)
    print("[TTS] Reloaded HiFi-GAN model.")

def reload_model():
    global tacotron2, hparams, hifigan, h, denoiser, hifigan_sr, h2, denoiser_sr
    tts_path = get_settings()["file_import_path"]
    hifigan_config = get_settings()["hifigan_config_path"]
    hifigan_path = get_settings()["hifigan_path"]

    load_TTS(tts_path, hifigan_path, hifigan_config, superres_path, superres_config)


def load_pronunciation_dict(dict_path=CMU_DICT_PATH):
    cmu = {}
    with open(dict_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            if len(parts) == 2:
                word, arpabet = parts
                cmu[word.upper()] = arpabet
    return cmu

cmu_dict = load_pronunciation_dict()

def ARPA(text, cmu_dict, punctuation=r"!?,.;", EOS_Token=True):
    output = ''
    for word_ in text.split(" "):
        word = word_
        end_chars = ''
        while any(c in word for c in punctuation) and len(word) > 1:
            if word[-1] in punctuation:
                end_chars = word[-1] + end_chars
                word = word[:-1]
            else:
                break
        try:
            word_arpa = cmu_dict[word.upper()]
            word = "{" + word_arpa + "}"
        except KeyError:
            pass
        output = (output + " " + word + end_chars).strip()
    if EOS_Token and output and output[-1] != ";":
        output += ";"
    return output

# Retry TTS if reach max decoder step or reach max value
def synthesize_once(tacotron2, sequence):
    outputs, hit_max_steps = tacotron2.inference(sequence)
    mel_outputs = outputs[0]
    mel_postnet = outputs[1]
    return mel_outputs, mel_postnet, hit_max_steps

def speak(text: str, test=False):
    if test:
        test_model()
        from kivy.app import App
        settings_screen = App.get_running_app().settings_screen
        (tts_path, max_decoder_steps, sample_rate, stop_threshold, hifigan_config_path, max_duration,
         superres_strength, use_pronunciation, hifigan_path, denoiser_strength) = settings_screen.get_TTS_value()
    else:
        max_duration = get_settings()["max_duration"]
        stop_threshold = get_settings()["stop_threshold"]
        superres_strength = get_settings()["superres_strength"]
        use_pronunciation = get_settings()["use_pronunciation"]
        denoiser_strength = get_settings()["denoiser_strength"]

    # dynamic decoder steps
    if use_pronunciation:
        text = ARPA(text, cmu_dict)

    sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
    sequence = torch.LongTensor(sequence)

    user_max_steps = max_duration * 80  # keep your setting as the hard cap
    seq_len = sequence.shape[1]

    pause_bonus = (
            text.count(",") * 15 +
            text.count(".") * 25 +
            text.count("?") * 25 +
            text.count("!") * 25 +
            text.count(";") * 20
    )

    estimated_steps = max(250, int(seq_len * 8.5) + pause_bonus)
    dynamic_steps = min(user_max_steps, estimated_steps)

    tacotron2.decoder.max_decoder_steps = dynamic_steps
    tacotron2.decoder.gate_threshold = stop_threshold

    print(
        f"[TTS] seq_len={seq_len}, "
        f"estimated_steps={estimated_steps}, "
        f"cap={user_max_steps}, "
        f"using={dynamic_steps}"
    )

    best_final = None

    best_final = None

    with torch.no_grad():
        for attempt in range(1, 4):
            mel_outputs, mel_postnet, hit_max_steps = synthesize_once(tacotron2, sequence)

            actual_steps = mel_postnet.shape[2]
            print(f"[TTS] actual_steps={actual_steps}")

            if hit_max_steps:
                print(f"[TTS] [{attempt}/3] Retrying... (hit_max_steps)")
                continue

            y_hat = hifigan(mel_postnet)
            audio = y_hat.squeeze().cpu().numpy() * MAX_WAV_VALUE
            audio = denoiser(torch.tensor(audio).unsqueeze(0), strength=denoiser_strength).squeeze().numpy()

            normalize = (MAX_WAV_VALUE / np.max(np.abs(audio))) ** 0.9
            audio *= normalize

            wave = resampy.resample(
                audio, h.sampling_rate, h2.sampling_rate,
                filter="sinc_window", window=scipy.signal.windows.hann, num_zeros=8
            )
            wave = wave / MAX_WAV_VALUE
            wave_tensor = torch.FloatTensor(wave).unsqueeze(0)

            mel_sr, bad_range, y_min, y_max = mel_spectrogram(
                wave_tensor,
                h2.n_fft,
                h2.num_mels,
                h2.sampling_rate,
                h2.hop_size,
                h2.win_size,
                h2.fmin,
                h2.fmax,
                return_range_status=True
            )

            y_sr = hifigan_sr(mel_sr).squeeze().cpu().numpy() * MAX_WAV_VALUE
            y_sr = denoiser_sr(torch.tensor(y_sr).unsqueeze(0), strength=denoiser_strength).squeeze().numpy()

            b = scipy.signal.firwin(101, cutoff=10500, fs=h2.sampling_rate, pass_zero=False)
            y_hp = scipy.signal.lfilter(b, [1.0], y_sr)
            y_hp *= superres_strength

            wave_out = (wave * MAX_WAV_VALUE).astype(np.int16)
            final = wave_out[:len(y_hp)] + y_hp[:len(wave_out)]
            final = final / normalize

            best_final = final

            if bad_range:
                print(f"[TTS] [{attempt}/3] Retrying... (bad_range, y_min={y_min:.4f}, y_max={y_max:.4f})")
                continue

            break
        else:
            print("[TTS] Using best attempt for final audio")
            final = best_final

        if final is None:
            print("[TTS] ERROR: No valid audio generated after retries.")
            return

        silence = np.zeros(int(h2.sampling_rate * 0.3), dtype=np.int16)
        final = np.concatenate([silence, final.astype(np.int16), silence])

        # print(f"[TTS] Speaking: \"{text}\"")
        silence = np.zeros(int(h2.sampling_rate * 0.3), dtype=np.int16)
        final = np.concatenate([silence, final.astype(np.int16), silence])

        volume = get_settings()["volume"]

        final = final * np.clip(volume, 0.0, 1.0)

        sd.play(final.astype(np.int16), samplerate=h2.sampling_rate)
        sd.wait()

# For testing speaking
if __name__ == "__main__":
    while True:
        input_speech = input("Speak: ")
        if input_speech == "KKK":
            break
        speak(input_speech)
