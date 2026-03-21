import math
import os
import random
import torch
import torch.utils.data
import numpy as np
from librosa.util import normalize
from scipy.io.wavfile import read
from librosa.filters import mel as librosa_mel_fn

MAX_WAV_VALUE = 32768.0


def load_wav(full_path):
    sampling_rate, data = read(full_path)
    return data, sampling_rate

def dynamic_range_compression_torch(x, C=1, clip_val=1e-5):
    return torch.log(torch.clamp(x, min=clip_val) * C)

def spectral_normalize_torch(magnitudes):
    output = dynamic_range_compression_torch(magnitudes)
    return output


mel_basis = {}
hann_window = {}


def mel_spectrogram(
    y, n_fft, num_mels, sampling_rate, hop_size, win_size, fmin, fmax,
    center=False, return_range_status=False
):
    y_min = float(torch.min(y))
    y_max = float(torch.max(y))

    bad_range = False
    if y_min < -1.0:
        print('[hifi_gan/meldataset.py]min value is ', torch.min(y))
        bad_range = True
    if y_max > 1.0:
        print('[hifi_gan/meldataset.py]max value is ', torch.max(y))
        bad_range = True

    global mel_basis, hann_window
    key = str(fmax) + '_' + str(y.device)

    if key not in mel_basis:
        mel = librosa_mel_fn(
            sr=sampling_rate,
            n_fft=n_fft,
            n_mels=num_mels,
            fmin=fmin,
            fmax=fmax
        )
        mel_basis[key] = torch.from_numpy(mel).float().to(y.device)
        hann_window[str(y.device)] = torch.hann_window(win_size).to(y.device)

    y = torch.nn.functional.pad(
        y.unsqueeze(1),
        (int((n_fft - hop_size) / 2), int((n_fft - hop_size) / 2)),
        mode='reflect'
    )
    y = y.squeeze(1)

    spec = torch.view_as_real(
        torch.stft(
            y,
            n_fft,
            hop_length=hop_size,
            win_length=win_size,
            window=hann_window[str(y.device)],
            center=center,
            pad_mode='reflect',
            normalized=False,
            onesided=True,
            return_complex=True
        )
    )

    spec = torch.sqrt(spec.pow(2).sum(-1) + (1e-9))
    spec = torch.matmul(mel_basis[key], spec)
    spec = spectral_normalize_torch(spec)

    if return_range_status:
        return spec, bad_range, y_min, y_max

    return spec

