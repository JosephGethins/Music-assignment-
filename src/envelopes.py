from __future__ import annotations

import numpy as np


def adsr_envelope(
    gate_duration_seconds: float,
    sample_rate: int,
    attack: float = 0.02,
    decay: float = 0.10,
    sustain_level: float = 0.65,
    release: float = 0.20,
) -> np.ndarray:
    """Create an offline ADSR envelope.

    The gate duration is the time before note-off. Release is appended after the
    gate, which better reflects note-on/note-off behaviour than treating release
    as part of the notated duration.
    """
    if gate_duration_seconds <= 0:
        raise ValueError("gate_duration_seconds must be positive")
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive")
    if min(attack, decay, release) < 0:
        raise ValueError("ADSR times cannot be negative")
    if not 0.0 <= sustain_level <= 1.0:
        raise ValueError("sustain_level must be between 0 and 1")

    gate_samples = max(1, round(gate_duration_seconds * sample_rate))
    attack_samples = min(round(attack * sample_rate), gate_samples)
    remaining = gate_samples - attack_samples
    decay_samples = min(round(decay * sample_rate), remaining)
    sustain_samples = gate_samples - attack_samples - decay_samples
    release_samples = round(release * sample_rate)

    parts = []
    if attack_samples:
        parts.append(np.linspace(0.0, 1.0, attack_samples, endpoint=False))
    if decay_samples:
        parts.append(
            np.linspace(1.0, sustain_level, decay_samples, endpoint=False)
        )
    if sustain_samples:
        parts.append(np.full(sustain_samples, sustain_level))
    if release_samples:
        parts.append(np.linspace(sustain_level, 0.0, release_samples, endpoint=True))

    return np.concatenate(parts).astype(np.float32)


def apply_fade(
    audio: np.ndarray,
    sample_rate: int,
    fade_in_seconds: float = 0.005,
    fade_out_seconds: float = 0.010,
) -> np.ndarray:
    """Apply short ramps to reduce clicks at event boundaries."""
    result = np.asarray(audio, dtype=np.float32).copy()
    if result.size == 0:
        return result

    fade_in = min(round(fade_in_seconds * sample_rate), result.size // 2)
    fade_out = min(round(fade_out_seconds * sample_rate), result.size // 2)

    if fade_in:
        result[:fade_in] *= np.linspace(0.0, 1.0, fade_in, endpoint=True)
    if fade_out:
        result[-fade_out:] *= np.linspace(1.0, 0.0, fade_out, endpoint=True)
    return result
