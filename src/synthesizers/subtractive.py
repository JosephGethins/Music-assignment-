from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from scipy.signal import butter, sawtooth, sosfilt, square

from .base import Synthesizer
from envelopes import adsr_envelope


class SubtractiveSynth(Synthesizer):
    """Subtractive synthesis, as in the lecture:
    sawtooth -> Butterworth low-pass (sosfilt) -> envelope.

    Parameters:
      waveform  "saw" (lecture) or "square"
      cutoff    low-pass cutoff in Hz, default 4000 (lecture)
      order     Butterworth filter order, default 4 (lecture)
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
        waveform = str(s.get("waveform", "saw"))
        cutoff = float(s.get("cutoff", 4000.0))
        order = int(s.get("order", 4))
        if waveform not in ("saw", "square"):
            raise ValueError("waveform must be 'saw' or 'square'")
        if not 20.0 <= cutoff < sample_rate / 2:
            raise ValueError("cutoff must be between 20 Hz and Nyquist")
        if not 1 <= order <= 12:
            raise ValueError("order must be between 1 and 12")

        envelope = adsr_envelope(
            gate_duration_seconds=gate_duration_seconds,
            sample_rate=sample_rate,
            attack=float(s.get("attack", 0.02)),
            decay=float(s.get("decay", 0.10)),
            sustain_level=float(s.get("sustain_level", 0.70)),
            release=float(s.get("release", 0.15)),
        )
        t = np.arange(envelope.size) / sample_rate

        # 1. Harmonically rich source
        phase = 2 * np.pi * frequency * t
        source = sawtooth(phase) if waveform == "saw" else square(phase)

        # 2. Low-pass filter (removes harmonics above the cutoff)
        sos = butter(order, cutoff, btype="lowpass", fs=sample_rate, output="sos")
        filtered = sosfilt(sos, source)

        # Lecture normalises the waveform shape; loudness comes from dynamic
        peak = np.max(np.abs(filtered))
        if peak > 0:
            filtered = filtered / peak

        return (dynamic * envelope * filtered).astype(np.float32)