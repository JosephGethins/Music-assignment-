from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

import numpy as np


class Synthesizer(ABC):
    """Common interface required by the shared timeline renderer."""

    @abstractmethod
    def render_voice(
        self,
        frequency: float,
        gate_duration_seconds: float,
        dynamic: float,
        articulation: str,
        sample_rate: int,
        parameters: Mapping[str, float] | None = None,
    ) -> np.ndarray:
        """Return one mono voice as floating-point samples."""
        raise NotImplementedError
