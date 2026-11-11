from __future__ import annotations

from pathlib import Path

import numpy as np

from audio_output import save_wav
from config import AudioConfig
from input_readers import read_midi
from synthesizers.additive import AdditiveSynth
from synthesizers.fm import FMSynth
from synthesizers.subtractive import SubtractiveSynth
from timeline import render_timeline

My_student_id = "23459886"   

SYNTHS = {
    "additive": AdditiveSynth(),
    "fm": FMSynth(),
    "subtractive": SubtractiveSynth(),
}


def check_audio(name: str, audio: np.ndarray, sample_rate: int) -> None:
    """Basic output validation: NaN, silence, clipping, length."""
    if not np.all(np.isfinite(audio)):
        raise ValueError(f"{name}: audio contains NaN or inf")
    peak = float(np.max(np.abs(audio)))
    if peak < 0.01:
        raise ValueError(f"{name}: output is effectively silent")
    if peak > 1.0:
        raise ValueError(f"{name}: output clips (peak {peak:.3f})")
    print(f"  {name}: {audio.size / sample_rate:.2f} s, peak {peak:.3f}  OK")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "output"
    out_dir.mkdir(exist_ok=True)

    config = AudioConfig(sample_rate=44_100, tempo_bpm=100.0)
    events = read_midi(root / "input" / "cs322_simple_melody.mid")
    print(f"Parsed {len(events)} events")

    for name, synth in SYNTHS.items():
        audio = render_timeline(events=events, synthesizer=synth, config=config)
        check_audio(name, audio, config.sample_rate)
        path = save_wav(str(out_dir / f"{My_student_id}_{name}.wav"), audio, config.sample_rate)
        print(f"  saved {path}")


if __name__ == "__main__":
    main()