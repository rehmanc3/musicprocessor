from __future__ import annotations
import numpy as np
import soundfile as sf
import librosa

TARGET_SR = 44100


def load_audio(path: str, sr: int = TARGET_SR) -> np.ndarray:
    # Returns float32 stereo [2, T]
    y, file_sr = librosa.load(path, sr=sr, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y], axis=0)
    if y.shape[0] != 2:  # Ensure [2, T]
        if y.shape[0] > 2:
            y = y[:2]
        else:
            y = np.vstack([y, y])
    return y.astype(np.float32)


def save_audio(path: str, audio: np.ndarray, sr: int = TARGET_SR):
    # audio: [2, T] float32
    audio = np.ascontiguousarray(audio.T)  # [T, 2]
    sf.write(path, audio, sr, subtype='PCM_16')


def pad_audio(x: np.ndarray, chunk: int) -> tuple[np.ndarray, int]:
    # Pad to multiple of chunk
    T = x.shape[-1]
    rem = (-T) % chunk
    if rem:
        x = np.pad(x, ((0,0),(0,rem)))
    return x, rem