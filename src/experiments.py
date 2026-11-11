from __future__ import annotations

from pathlib import Path

from audio_output import save_wav
from config import AudioConfig
from input_readers import read_midi
from synthesizers.additive import AdditiveSynth
from synthesizers.fm import FMSynth
from synthesizers.subtractive import SubtractiveSynth
from timeline import render_timeline

# (technique, synth, label, parameters). {} = defaults (the lecture values).
EXPERIMENTS = [
    ("additive", AdditiveSynth(), "baseline", {}),
    ("additive", AdditiveSynth(), "flat_amplitudes", {"amplitudes": [1.0, 1.0, 1.0, 1.0]}),
    ("additive", AdditiveSynth(), "inharmonic_ratios", {"ratios": [1.0, 2.76, 5.40, 8.93]}),

    ("fm", FMSynth(), "baseline", {}),
    ("fm", FMSynth(), "ratio3.5", {"ratio": 3.5}),
    ("fm", FMSynth(), "index1", {"index": 1.0}),

    ("subtractive", SubtractiveSynth(), "baseline", {}),
    ("subtractive", SubtractiveSynth(), "cutoff800", {"cutoff": 800.0}),
    ("subtractive", SubtractiveSynth(), "square", {"waveform": "square"}),
]


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "output" / "experiments"
    out_dir.mkdir(parents=True, exist_ok=True)

    config = AudioConfig(sample_rate=44_100, tempo_bpm=100.0)
    events = read_midi(root / "input" / "cs322_simple_melody.mid")

    for technique, synth, label, params in EXPERIMENTS:
        audio = render_timeline(events=events, synthesizer=synth,
                                config=config, parameters=params)
        save_wav(str(out_dir / f"{technique}_{label}.wav"), audio, config.sample_rate)
        print(f"saved {technique}_{label}.wav")


if __name__ == "__main__":
    main()