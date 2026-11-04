from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy.io import wavfile


def save_wav(path: str | Path, audio: np.ndarray, sample_rate: int) -> Path:
    """Save mono floating-point audio as 16-bit PCM WAV."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    samples = np.asarray(audio, dtype=np.float32)
    if samples.ndim != 1:
        raise ValueError("save_wav currently expects mono audio")
    if not np.all(np.isfinite(samples)):
        raise ValueError("Audio contains NaN or infinite values")
    clipped = np.clip(samples, -1.0, 1.0)
    pcm16 = (clipped * np.iinfo(np.int16).max).astype(np.int16)
    wavfile.write(output_path, sample_rate, pcm16)
    return output_path.resolve()


def play_audio(audio: np.ndarray, sample_rate: int) -> None:
    """Optional playback. WAV export remains the assessed requirement."""
    try:
        import sounddevice as sd
    except ImportError:
        print("Playback skipped: install sounddevice to enable it")
        return

    sd.play(np.asarray(audio, dtype=np.float32), sample_rate)
    sd.wait()
