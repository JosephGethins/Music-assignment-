from __future__ import annotations

from dataclasses import dataclass


REST_NAMES = {"REST", "R", "Z"}
SUPPORTED_ARTICULATIONS = {"normal", "staccato", "legato"}


@dataclass(frozen=True)
class MusicalEvent:
    """Shared representation used by every input reader and synthesizer."""

    pitch: str
    onset_beats: float
    duration_beats: float
    dynamic: float = 0.8
    articulation: str = "normal"

    def __post_init__(self) -> None:
        normalized_pitch = self.pitch.strip()
        normalized_articulation = self.articulation.strip().lower()

        if not normalized_pitch:
            raise ValueError("pitch cannot be empty")
        if self.onset_beats < 0:
            raise ValueError("onset_beats cannot be negative")
        if self.duration_beats <= 0:
            raise ValueError("duration_beats must be positive")
        if not 0.0 <= self.dynamic <= 1.0:
            raise ValueError("dynamic must be between 0.0 and 1.0")
        if normalized_articulation not in SUPPORTED_ARTICULATIONS:
            raise ValueError(
                f"Unsupported articulation: {self.articulation}. "
                f"Choose from {sorted(SUPPORTED_ARTICULATIONS)}"
            )

        object.__setattr__(self, "pitch", normalized_pitch)
        object.__setattr__(self, "articulation", normalized_articulation)

    @property
    def is_rest(self) -> bool:
        return self.pitch.upper() in REST_NAMES

    @property
    def end_beats(self) -> float:
        return self.onset_beats + self.duration_beats


def from_dictionary(data: dict) -> MusicalEvent:
    """Convert the lecture dictionary structure into a validated event."""
    required = {"pitch", "onset_beats", "duration_beats"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"Missing event fields: {sorted(missing)}")

    return MusicalEvent(
        pitch=str(data["pitch"]),
        onset_beats=float(data["onset_beats"]),
        duration_beats=float(data["duration_beats"]),
        dynamic=float(data.get("dynamic", 0.8)),
        articulation=str(data.get("articulation", "normal")),
    )
