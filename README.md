# CS322 Assignment 1: From Symbolic Music to Multi-Synthesis Audio

Student: Joseph Gethins
ID: 23459886

Reads the supplied MIDI melody, renders it with three synthesis techniques (additive, FM, subtractive) through one shared timeline and mixer. Also includes 3 parameter experiments per synthesis (9 in total including the original baseline additive, subtractive and fm) and a creative extension (selectable configurations plus analysis plots).

## Requirements

- Python 3.13
- Packages in `requirements.txt`:
- numpy: audio arrays and maths
- scipy: oscillators and the low pass filter
- mido: parses the MIDI file
- matplotlib: analysis plots in the extension for the creative part

## Setup

From the project root (the folder containing `src/` and `input/`), run these commands step by step. First two activates the venv enviroment, the third and last downloads all the requirments from the text file that the programs need to run.

Windows (PowerShell):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Below is what you should see if you need to rerun the files, The first should ouput 3 wav files with my student ID and named additive, fm and subtractive in that order in the folder named output

1. Final renders (the three required WAV files):

   ```
   python src/main.py
   ```

   Expected: "Parsed 8 events", then three OK lines for each (additive, fm, subtractive),
   Files are written to `output/`: `<23459886>_additive.wav`, `<23459886>_fm.wav`, `<23459886>_subtractive.wav`.

2. Parameter experiments:

   ```
   python src/experiments.py
   ```

   Writes 9 WAV files (a baseline plus two changed settings per technique) to
   `output/experiments/`.
   The file that writes the expirments is located at: `src/experiments.py`.

3. Creative extension:

   Here at the steps to recreate the 2 png files and 6 wav files it uses to create the graphs in output/extension. They are already there but if needed they can be recreated step by step below

   ```
   python src/extension.py --list
   python src/extension.py
   python src/extension.py --preset dark
   python src/extension.py --synth fm --set ratio=3.5 --set index=2
   ```

   Writes 6 wav files and 2 `analysis.png` (waveform, spectrum, spectrogram) to `output/extension/`.

## Project structure

```
input/cs322_simple_melody.mid   supplied melody from moodle (the file the program reads)
src/input_readers.py            MIDI parsing (read_midi)
src/event_model.py              MusicalEvent data structure
src/music_utils.py              pitch, beat, time conversions
src/timeline.py                 shared timeline, mixing, peak protection
src/envelopes.py                ADSR envelope
src/synthesizers/               base interface + additive.py, fm.py, subtractive.py
src/audio_output.py             WAV export
src/main.py                     final renders and output checks
src/experiments.py              parameter experiments
src/extension.py, presets.py    creative extension
output/                         generated audio and plots in their respective folders
```

## Notes

- Input: the melody is read from `input/cs322_simple_melody.mid`; nothing is hard-coded so technically the melody can be changed avd everything should work as long as the name is the same.
- Tempo is set to 100 BPM in `AudioConfig` (not read from file).
- Sample rate is 44,100 Hz.
- Code reuse, libraries and assistance are declared in section A9 of the report.