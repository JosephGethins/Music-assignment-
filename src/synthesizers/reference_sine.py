from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .base import Synthesizer
from envelopes import adsr_envelope


class ReferenceSineSynth(Synthesizer):
    """Reference voice used only to test the common pipeline.

    This is a building block, not one of the three submitted synthesis methods.
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

        settings = dict(parameters or {})
        release = float(settings.get("release", 0.12))
        envelope = adsr_envelope(
            gate_duration_seconds=gate_duration_seconds,
            sample_rate=sample_rate,
            attack=float(settings.get("attack", 0.01)),
            decay=float(settings.get("decay", 0.08)),
            sustain_level=float(settings.get("sustain_level", 0.70)),
            release=release,
        )
        time = np.arange(envelope.size) / sample_rate
        return (dynamic * envelope * np.sin(2 * np.pi * frequency * time)).astype(
            np.float32
        )
