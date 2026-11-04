from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .base import Synthesizer
from envelopes import adsr_envelope

# Lecture defaults (additive_synthesis.py): harmonics 1-4 at these amplitudes
DEFAULT_AMPLITUDES = (1.0, 0.5, 0.3, 0.2)


class AdditiveSynth(Synthesizer):
    """Additive synthesis: sum of sine partials.

    Parameters:
      amplitudes  sequence of floats, one per partial (default: lecture 1, .5, .3, .2)
                  Its length is the partial count.
      ratios      sequence of floats, partial frequency / fundamental, same length
                  as amplitudes (default: harmonic 1, 2, 3, ...). Non-integer
                  values give an inharmonic, bell-like sound.
      attack, decay, sustain_level, release   ADSR (seconds / 0..1)
    """

    def render_voice(
        self,
        frequency: float,
        gate_duration_seconds: float,
        dynamic: float,
        articulation: str,
        sample_rate: int,
        parameters: Mapping[str, float] | None = None,
    ) -> np.ndarray:
        if frequency <= 0:
            raise ValueError("frequency must be positive")
        if not 0.0 <= dynamic <= 1.0:
            raise ValueError("dynamic must be between 0 and 1")

        s = dict(parameters or {})
        amplitudes = np.asarray(s.get("amplitudes", DEFAULT_AMPLITUDES), dtype=float)
        ratios = np.asarray(
            s.get("ratios", np.arange(1, amplitudes.size + 1)), dtype=float
        )
        if amplitudes.ndim != 1 or amplitudes.size < 1:
            raise ValueError("amplitudes must be a non-empty 1-D sequence")
        if ratios.shape != amplitudes.shape:
            raise ValueError("ratios and amplitudes must have the same length")
        if np.any(amplitudes < 0) or not np.any(amplitudes > 0):
            raise ValueError("amplitudes must be >= 0 and not all zero")
        if np.any(ratios <= 0):
            raise ValueError("ratios must be positive")

        envelope = adsr_envelope(
            gate_duration_seconds=gate_duration_seconds,
            sample_rate=sample_rate,
            attack=float(s.get("attack", 0.02)),
            decay=float(s.get("decay", 0.10)),
            sustain_level=float(s.get("sustain_level", 0.70)),
            release=float(s.get("release", 0.15)),
        )
        t = np.arange(envelope.size) / sample_rate

        # Core algorithm: add up the partials (skip any above Nyquist)
        signal = np.zeros(envelope.size)
        for amp, ratio in zip(amplitudes, ratios):
            f = ratio * frequency
            if f >= sample_rate / 2:
                continue
            signal += amp * np.sin(2 * np.pi * f * t)

        # Lecture normalises the waveform shape; loudness comes from dynamic
        peak = np.max(np.abs(signal))
        if peak > 0:
            signal /= peak

        return (dynamic * envelope * signal).astype(np.float32)