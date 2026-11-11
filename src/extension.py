"""Creative extension: user-selectable synthesis configuration + analysis plots.

Pick a synth and a preset (and/or override single parameters) from the command
line. The tool renders the supplied melody through the shared timeline, saves a
WAV, and draws waveform, spectrum and spectrogram so the timbre can be compared
visually, not just by ear.

Examples (run from the project root):
    python src/extension.py --list
    python src/extension.py                               # all synths, default preset
    python src/extension.py --preset dark                 # all synths, "dark" preset
    python src/extension.py --synth fm --set ratio=3.5 --set index=2
"""
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw straight to a PNG file, no window needed
import matplotlib.pyplot as plt
import numpy as np

from audio_output import save_wav
from config import AudioConfig
from input_readers import read_midi
from presets import PRESETS, VALID_PARAMS
from synthesizers.additive import AdditiveSynth
from synthesizers.fm import FMSynth
from synthesizers.subtractive import SubtractiveSynth
from timeline import render_timeline

SYNTHS = {"additive": AdditiveSynth, "fm": FMSynth, "subtractive": SubtractiveSynth}

FFT_SIZE = 2048      # samples per analysis frame (spectrogram)
HOP = 512            # step between frames
SPECTRUM_FRAME = 4096
DB_FLOOR = -80.0     # quietest level drawn, in dB below the loudest bin
MAX_HZ = 8000        # upper frequency shown in the plots


def parse_override(text: str) -> tuple[str, object]:
    """'ratio=3.5' -> ('ratio', 3.5); 'amplitudes=[1,0.5]' -> list; 'waveform=square' -> str."""
    if "=" not in text:
        raise ValueError(f"--set expects KEY=VALUE, got '{text}'")
    key, raw = text.split("=", 1)
    try:
        value = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        value = raw  # plain word such as square
    return key.strip(), value


def spectrum_db(audio: np.ndarray, sample_rate: int, start_seconds: float):
    """Spectrum of one Hann-windowed frame (same method as the lecture)."""
    start = int(start_seconds * sample_rate)
    frame = audio[start:start + SPECTRUM_FRAME]
    frame = np.pad(frame, (0, SPECTRUM_FRAME - len(frame)))
    magnitude = np.abs(np.fft.rfft(frame * np.hanning(SPECTRUM_FRAME)))
    freqs = np.fft.rfftfreq(SPECTRUM_FRAME, d=1.0 / sample_rate)
    level = np.maximum(magnitude / max(magnitude.max(), 1e-12), 10 ** (DB_FLOOR / 20))
    return freqs, 20 * np.log10(level)


def spectrogram_db(audio: np.ndarray) -> np.ndarray:
    """Short-time Fourier transform in dB (rows = frequency, columns = time)."""
    window = np.hanning(FFT_SIZE)
    padded = np.pad(audio, (0, FFT_SIZE))
    frames = np.array([padded[i:i + FFT_SIZE] * window for i in range(0, len(audio), HOP)])
    magnitude = np.abs(np.fft.rfft(frames, axis=1)).T
    level = np.maximum(magnitude / max(magnitude.max(), 1e-12), 10 ** (DB_FLOOR / 20))
    return 20 * np.log10(level)


def plot_analysis(results, sample_rate: int, frame_time: float, path: Path) -> None:
    """One row per synth: waveform | spectrum at frame_time | spectrogram."""
    fig, axes = plt.subplots(len(results), 3, figsize=(16, 3.4 * len(results)), squeeze=False)
    for row, (name, params, audio) in zip(axes, results):
        label = f"{name} {params if params else '(defaults)'}"
        t = np.arange(len(audio)) / sample_rate

        row[0].plot(t, audio, linewidth=0.5)
        row[0].set_title(f"{label}\nwaveform")
        row[0].set_xlabel("Time (s)")
        row[0].set_ylabel("Amplitude")

        freqs, db = spectrum_db(audio, sample_rate, frame_time)
        row[1].plot(freqs, db)
        row[1].set_xlim(0, MAX_HZ)
        row[1].set_ylim(DB_FLOOR, 0)
        row[1].set_title(f"spectrum at {frame_time:.2f} s")
        row[1].set_xlabel("Frequency (Hz)")
        row[1].set_ylabel("dB")

        spec = spectrogram_db(audio)
        bins = int(MAX_HZ / (sample_rate / FFT_SIZE))
        row[2].imshow(spec[:bins], origin="lower", aspect="auto", cmap="magma",
                      extent=[0, len(audio) / sample_rate, 0, MAX_HZ])
        row[2].set_title("spectrogram")
        row[2].set_xlabel("Time (s)")
        row[2].set_ylabel("Frequency (Hz)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render and analyse the melody with a chosen synth configuration.")
    parser.add_argument("--synth", default="all", choices=[*SYNTHS, "all"])
    parser.add_argument("--preset", default="default")
    parser.add_argument("--set", dest="overrides", action="append", default=[], metavar="KEY=VALUE",
                        help="override one parameter, e.g. --set cutoff=800")
    parser.add_argument("--frame-time", type=float, default=0.3,
                        help="time (s) of the frame used for the spectrum plot")
    parser.add_argument("--list", action="store_true", help="list synths, presets and parameters")
    args = parser.parse_args()

    if args.list:
        for name, presets in PRESETS.items():
            print(f"{name}: presets {sorted(presets)}; parameters {sorted(VALID_PARAMS[name])}")
        return

    names = list(SYNTHS) if args.synth == "all" else [args.synth]
    try:
        overrides = dict(parse_override(o) for o in args.overrides)
        for key in overrides:
            if not any(key in VALID_PARAMS[n] for n in names):
                raise ValueError(f"unknown parameter '{key}' for {names}; use --list to see valid names")
        for n in names:
            if args.preset not in PRESETS[n]:
                raise ValueError(f"preset '{args.preset}' not found for {n}; choose from {sorted(PRESETS[n])}")
        if args.frame_time < 0:
            raise ValueError("--frame-time cannot be negative")

        root = Path(__file__).resolve().parent.parent
        out_dir = root / "output" / "extension"
        out_dir.mkdir(parents=True, exist_ok=True)
        config = AudioConfig(sample_rate=44_100, tempo_bpm=100.0)
        events = read_midi(root / "input" / "cs322_simple_melody.mid")

        tag = args.preset + ("_custom" if overrides else "")
        results = []
        for n in names:
            params = {**PRESETS[n][args.preset], **{k: v for k, v in overrides.items() if k in VALID_PARAMS[n]}}
            audio = render_timeline(events=events, synthesizer=SYNTHS[n](), config=config, parameters=params)
            wav = save_wav(str(out_dir / f"{n}_{tag}.wav"), audio, config.sample_rate)
            print(f"saved {wav}")
            results.append((n, params, audio))

        png = out_dir / f"analysis_{args.synth}_{tag}.png"
        plot_analysis(results, config.sample_rate, args.frame_time, png)
        print(f"saved {png}")
    except (ValueError, FileNotFoundError) as error:
        sys.exit(f"Error: {error}")


if __name__ == "__main__":
    main()