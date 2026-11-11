"""Named synthesis configurations for the extension tool (extension.py).

A preset is just a `parameters` dict that is passed to render_timeline, so the
same settings work for any synth that understands those keys.
"""
from __future__ import annotations

# Parameters each synth accepts (used to catch typos in --set KEY=VALUE).
VALID_PARAMS = {
    "additive": {"amplitudes", "ratios", "attack", "decay", "sustain_level", "release"},
    "fm": {"ratio", "index", "attack", "decay", "sustain_level", "release"},
    "subtractive": {"waveform", "cutoff", "order", "attack", "decay", "sustain_level", "release"},
}

# {} means "use the synth's own defaults" (the lecture values).
PRESETS = {
    "additive": {
        "default": {},
        "dark": {"amplitudes": [1.0, 0.25, 0.10, 0.05]},      # highs much quieter
        "bright": {"amplitudes": [1.0] * 6},                  # six equal partials
    },
    "fm": {
        "default": {},
        "dark": {"index": 1.0},                               # little modulation
        "bright": {"index": 8.0},                             # lots of sidebands
    },
    "subtractive": {
        "default": {},
        "dark": {"cutoff": 800.0},                            # filter closed
        "bright": {"cutoff": 8000.0},                         # filter open
    },
}