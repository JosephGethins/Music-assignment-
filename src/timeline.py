from __future__ import annotations

from collections.abc import Iterable, Mapping

import numpy as np

from config import AudioConfig
from event_model import MusicalEvent
from music_utils import articulation_ratio, beats_to_samples, beats_to_seconds, pitch_to_frequency
from synthesizers.base import Synthesizer


def apply_peak_protection(audio: np.ndarray, peak_limit: float = 0.95) -> np.ndarray:
    """Scale only when the signal exceeds the chosen peak limit."""
    result = np.asarray(audio, dtype=np.float32)
    if result.size == 0:
        return result
    peak = float(np.max(np.abs(result)))
    if peak > peak_limit and peak > 0.0:
        result = result * (peak_limit / peak)
    return result.astype(np.float32)


def render_timeline(
    events: Iterable[MusicalEvent],
    synthesizer: Synthesizer,
    config: AudioConfig,
    parameters: Mapping[str, float] | None = None,
) -> np.ndarray:
    """Render notes and chords onto one shared mono timeline.

    Release tails are preserved by dynamically growing the output array.
    """
    ordered_events = sorted(events, key=lambda event: event.onset_beats)
    if not ordered_events:
        raise ValueError("No musical events were supplied")

    initial_end_beats = max(event.end_beats for event in ordered_events)
    output = np.zeros(
        beats_to_samples(initial_end_beats, config.tempo_bpm, config.sample_rate),
        dtype=np.float32,
    )

    for event in ordered_events:
        if event.is_rest:
            continue

        frequency = pitch_to_frequency(event.pitch)
        gate_beats = event.duration_beats * articulation_ratio(event.articulation)
        gate_seconds = beats_to_seconds(gate_beats, config.tempo_bpm)
        voice = synthesizer.render_voice(
            frequency=frequency,
            gate_duration_seconds=gate_seconds,
            dynamic=event.dynamic,
            articulation=event.articulation,
            sample_rate=config.sample_rate,
            parameters=parameters,
        )
        voice = np.asarray(voice, dtype=np.float32)
        if voice.ndim != 1:
            raise ValueError("Each voice must be returned as a one-dimensional mono array")
        if not np.all(np.isfinite(voice)):
            raise ValueError(f"Non-finite samples generated for event {event}")

        start = beats_to_samples(event.onset_beats, config.tempo_bpm, config.sample_rate)
        end = start + voice.size
        if end > output.size:
            output = np.pad(output, (0, end - output.size))
        output[start:end] += voice

    return apply_peak_protection(output, config.peak_limit)
