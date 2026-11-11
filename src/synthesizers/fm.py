from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .base import Synthesizer
from envelopes import adsr_envelope


class FMSynth(Synthesizer):
    """Two-operator FM, as in the lecture:
    y(t) = sin(2*pi*fc*t + I * sin(2*pi*fm*t)),  fm = ratio * fc

    Parameters:
      ratio   modulator / carrier frequency, default 2.0 (lecture)
      index   modulation index I, default 5.0 (lecture)
      attack, decay, sustain_level, release   ADSR for amplitude
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
        ratio = float(s.get("ratio", 2.0))
        index = float(s.get("index", 5.0))
        if ratio <= 0:
            raise ValueError("ratio must be positive")
        if index < 0:
            raise ValueError("index must be >= 0")

        envelope = adsr_envelope(
            gate_duration_seconds=gate_duration_seconds,
            sample_rate=sample_rate,
            attack=float(s.get("attack", 0.01)),
            decay=float(s.get("decay", 0.10)),
            sustain_level=float(s.get("sustain_level", 0.70)),
            release=float(s.get("release", 0.15)),
        )
        t = np.arange(envelope.size) / sample_rate

        modulator = np.sin(2 * np.pi * (ratio * frequency) * t)
        signal = np.sin(2 * np.pi * frequency * t + index * modulator)

        return (dynamic * envelope * signal).astype(np.float32)