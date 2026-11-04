from __future__ import annotations

import re

NOTE_PATTERN = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")
PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
}


def pitch_to_semitone_number(pitch_name: str) -> int:
    """Return an absolute semitone number where C4 is 60 and A4 is 69."""
    match = NOTE_PATTERN.fullmatch(pitch_name.strip())
    if match is None:
        raise ValueError(
            f"Invalid pitch name: {pitch_name!r}. Examples: C4, F#4, Bb3"
        )

    letter, accidental, octave_text = match.groups()
    pitch_class_name = (letter + accidental).upper()
    octave = int(octave_text)
    return 12 * (octave + 1) + PITCH_CLASS[pitch_class_name]


def pitch_to_frequency(pitch_name: str, reference_frequency: float = 440.0) -> float:
    """Convert a pitch name to equal-tempered frequency using A4 = 440 Hz."""
    if reference_frequency <= 0:
        raise ValueError("reference_frequency must be positive")
    semitone_number = pitch_to_semitone_number(pitch_name)
    return reference_frequency * 2.0 ** ((semitone_number - 69) / 12.0)


def beats_to_seconds(beats: float, tempo_bpm: float) -> float:
    if beats < 0:
        raise ValueError("beats cannot be negative")
    if tempo_bpm <= 0:
        raise ValueError("tempo_bpm must be positive")
    return beats * 60.0 / tempo_bpm


def beats_to_samples(beats: float, tempo_bpm: float, sample_rate: int) -> int:
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    return round(beats_to_seconds(beats, tempo_bpm) * sample_rate)


def articulation_ratio(name: str) -> float:
    """Simple lecture mapping from articulation to sounding-duration ratio."""
    ratios = {"staccato": 0.50, "normal": 0.90, "legato": 1.00}
    try:
        return ratios[name.strip().lower()]
    except KeyError as error:
        raise ValueError(f"Unsupported articulation: {name}") from error
