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

tacotron2_path = "tts_models/GLaDOS-146" #change the voice model path here
hifigan_path = "tts_models/g_02500000"
superres_path = "tts_models/Superres_Twilight_33000"
hifigan_config = "hifi_gan/config_v1.json"
superres_config = "hifi_gan/config_32k.json"
CMU_DICT_PATH = "cmudict/merged.dict.txt"

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
    hparams.sampling_rate = 22050
    hparams.max_decoder_steps = 3000
    hparams.gate_threshold = 0.25
    model = Tacotron2(hparams)
    checkpoint = torch.load(model_path, map_location="cpu")
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    return model, hparams

print("[TTS] Loading models...")
tacotron2, hparams = load_tacotron2(tacotron2_path)
hifigan, h, denoiser = load_hifigan(hifigan_path, hifigan_config)
hifigan_sr, h2, denoiser_sr = load_hifigan(superres_path, superres_config)
print("[TTS] Models loaded.")

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

def speak(text: str, max_duration=20, stop_threshold=0.9, superres_strength=10, use_pronunciation=True):
    if use_pronunciation:
        text = ARPA(text, cmu_dict)
    tacotron2.decoder.max_decoder_steps = max_duration * 80
    tacotron2.decoder.gate_threshold = stop_threshold

    sequence = np.array(text_to_sequence(text, ['english_cleaners']))[None, :]
    sequence = torch.LongTensor(sequence)

    with torch.no_grad():
        mel_outputs, mel_postnet, _, _ = tacotron2.inference(sequence)
        y_hat = hifigan(mel_postnet)
        audio = y_hat.squeeze().cpu().numpy() * MAX_WAV_VALUE
        audio = denoiser(torch.tensor(audio).unsqueeze(0), strength=35).squeeze().numpy()

        normalize = (MAX_WAV_VALUE / np.max(np.abs(audio))) ** 0.9
        audio *= normalize

        wave = resampy.resample(audio, h.sampling_rate, h2.sampling_rate,
                                filter="sinc_window", window=scipy.signal.windows.hann, num_zeros=8)
        wave = wave / MAX_WAV_VALUE
        wave_tensor = torch.FloatTensor(wave).unsqueeze(0)
        mel_sr = mel_spectrogram(wave_tensor, h2.n_fft, h2.num_mels, h2.sampling_rate,
                                 h2.hop_size, h2.win_size, h2.fmin, h2.fmax)

        y_sr = hifigan_sr(mel_sr).squeeze().cpu().numpy() * MAX_WAV_VALUE
        y_sr = denoiser_sr(torch.tensor(y_sr).unsqueeze(0), strength=35).squeeze().numpy()

        b = scipy.signal.firwin(101, cutoff=10500, fs=h2.sampling_rate, pass_zero=False)
        y_hp = scipy.signal.lfilter(b, [1.0], y_sr)
        y_hp *= superres_strength

        wave_out = (wave * MAX_WAV_VALUE).astype(np.int16)
        final = wave_out[:len(y_hp)] + y_hp[:len(wave_out)]
        final = final / normalize

        # print(f"[TTS] Speaking: \"{text}\"")
        silence = np.zeros(int(h2.sampling_rate * 0.3), dtype=np.int16)
        final = np.concatenate([silence, final.astype(np.int16), silence])

        sd.play(final, samplerate=h2.sampling_rate)
        sd.wait()
