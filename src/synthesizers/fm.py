from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .base import Synthesizer
from envelopes import adsr_envelope


class FMSynth(Synthesizer):
    """Two-operator FM, as in the lecture:
    y(t) = sin(2*pi*fc*t + I * sin(2*pi*fm*t)),  fm = ratio * fc

    Parameters:
      ratio        modulator / carrier frequency, default 2.0 (lecture)
      index        modulation index I, default 5.0 (lecture)
      index_end    OPTIONAL extension: if given, the index decays from `index`
                   to `index_end`. Default None = constant index (lecture).
      index_decay  time constant (s) of that decay, default 0.3
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
        index_end = s.get("index_end")
        index_end = index if index_end is None else float(index_end)
        index_decay = float(s.get("index_decay", 0.3))
        if ratio <= 0:
            raise ValueError("ratio must be positive")
        if index < 0 or index_end < 0:
            raise ValueError("index values must be >= 0")
        if index_decay <= 0:
            raise ValueError("index_decay must be positive")

        envelope = adsr_envelope(
            gate_duration_seconds=gate_duration_seconds,
            sample_rate=sample_rate,
            attack=float(s.get("attack", 0.01)),
            decay=float(s.get("decay", 0.10)),
            sustain_level=float(s.get("sustain_level", 0.70)),
            release=float(s.get("release", 0.15)),
        )
        t = np.arange(envelope.size) / sample_rate

        # Equal to `index` throughout unless index_end is set
        index_env = index_end + (index - index_end) * np.exp(-t / index_decay)

        modulator = np.sin(2 * np.pi * (ratio * frequency) * t)
        signal = np.sin(2 * np.pi * frequency * t + index_env * modulator)

        return (dynamic * envelope * signal).astype(np.float32)