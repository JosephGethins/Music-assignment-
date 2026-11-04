from dataclasses import dataclass


@dataclass(frozen=True)
class AudioConfig:
    """Immutable audio and tempo configuration."""

    sample_rate: int = 44_100
    tempo_bpm: float = 100.0
    peak_limit: float = 0.95

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if self.tempo_bpm <= 0:
            raise ValueError("tempo_bpm must be positive")
        if not 0.0 < self.peak_limit <= 1.0:
            raise ValueError("peak_limit must be in (0, 1]")
