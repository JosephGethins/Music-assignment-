EXPERIMENTS = [
    # Additive: partial amplitudes/count, and partial ratios (harmonic vs inharmonic)
    ("additive", AdditiveSynth(), "baseline", {}),
    ("additive", AdditiveSynth(), "flat_amps", {"amplitudes": [1.0, 1.0, 1.0, 1.0]}),
    ("additive", AdditiveSynth(), "eight_partials",
        {"amplitudes": [1.0, 0.5, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05]}),
    ("additive", AdditiveSynth(), "inharmonic",
        {"ratios": [1.0, 2.76, 5.40, 8.93]}),

    # FM: carrier-modulator ratio, modulation index, and the index envelope
    ("fm", FMSynth(), "baseline", {}),
    ("fm", FMSynth(), "ratio3.5", {"ratio": 3.5}),
    ("fm", FMSynth(), "index1", {"index": 1.0}),
    ("fm", FMSynth(), "index_decay", {"index": 5.0, "index_end": 0.5}),

    # Subtractive: cutoff, filter order, waveform
    ("subtractive", SubtractiveSynth(), "baseline", {}),
    ("subtractive", SubtractiveSynth(), "cutoff800", {"cutoff": 800.0}),
    ("subtractive", SubtractiveSynth(), "cutoff800_order1", {"cutoff": 800.0, "order": 1}),
    ("subtractive", SubtractiveSynth(), "square", {"waveform": "square"}),
]