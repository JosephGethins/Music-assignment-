from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from .base import Synthesizer


class TechniqueTemplate(Synthesizer):
    """Copy this file once for each selected synthesis technique."""

    def render_voice(
        self,
        frequency: float,
        gate_duration_seconds: float,
        dynamic: float,
        articulation: str,
        sample_rate: int,
        parameters: Mapping[str, float] | None = None,
    ) -> np.ndarray:
        # TODO 1: Validate technique-specific parameters.
        # TODO 2: Implement the defining synthesis algorithm.
        # TODO 3: Apply articulation and a suitable envelope or fade.
        # TODO 4: Return float32 audio. Do not normalize every note automatically.
        raise NotImplementedError("Implement one selected synthesis technique")
