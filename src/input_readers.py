from __future__ import annotations

from pathlib import Path

from event_model import MusicalEvent

DEFAULT_DYNAMIC = 0.8
DEFAULT_ARTICULATION = "normal"


def read_with_music21(path: str | Path) -> list[MusicalEvent]:
    """Starter adapter for ABC or MusicXML using music21.

    TODO: Test this function against the supplied files. Extend it if your file
    contains chords, multiple parts, multiple voices, dynamics, or articulations.
    Document any defaults used.
    """
    from music21 import chord, converter, note

    score = converter.parse(str(path))
    events: list[MusicalEvent] = []

    for element in score.flatten().notesAndRests:
        onset = float(element.offset)
        duration = float(element.quarterLength)

        if isinstance(element, note.Rest):
            events.append(
                MusicalEvent("REST", onset, duration, 0.0, DEFAULT_ARTICULATION)
            )
        elif isinstance(element, note.Note):
            dynamic = (
                float(element.volume.velocityScalar)
                if element.volume.velocityScalar is not None
                else DEFAULT_DYNAMIC
            )
            events.append(
                MusicalEvent(
                    element.pitch.nameWithOctave,
                    onset,
                    duration,
                    dynamic,
                    DEFAULT_ARTICULATION,
                )
            )
        elif isinstance(element, chord.Chord):
            # Notes in a chord share onset and duration.
            for pitch in element.pitches:
                events.append(
                    MusicalEvent(
                        pitch.nameWithOctave,
                        onset,
                        duration,
                        DEFAULT_DYNAMIC,
                        DEFAULT_ARTICULATION,
                    )
                )

    if not events:
        raise ValueError(f"No notes or rests were found in {path}")
    return events


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_name(number: int) -> str:
    """MIDI 60 -> 'C4' (octave = number // 12 - 1)."""
    return f"{NOTE_NAMES[number % 12]}{number // 12 - 1}"


def read_midi(path: str | Path) -> list[MusicalEvent]:
    from mido import MidiFile

    midi_file = MidiFile(str(path))
    ticks_per_beat = midi_file.ticks_per_beat
    events: list[MusicalEvent] = []

    for track in midi_file.tracks:
        tick = 0          # absolute time; msg.time is only a delta
        active = {}       # (channel, note) -> list of (start_tick, velocity)

        for msg in track:
            tick += msg.time
            is_on = msg.type == "note_on" and msg.velocity > 0
            is_off = msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0)

            if is_on:
                active.setdefault((msg.channel, msg.note), []).append((tick, msg.velocity))
            elif is_off:
                stack = active.get((msg.channel, msg.note))
                if not stack:
                    continue  # note_off with no matching note_on
                start, velocity = stack.pop(0)
                events.append(
                    MusicalEvent(
                        midi_to_name(msg.note),
                        start / ticks_per_beat,
                        (tick - start) / ticks_per_beat,
                        velocity / 127.0,
                        DEFAULT_ARTICULATION,
                    )
                )

    if not events:
        raise ValueError(f"No notes found in {path}")
    events.sort(key=lambda e: (e.onset_beats, e.pitch))
    return events
