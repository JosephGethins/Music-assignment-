# CS322 Assignment Starter Pack

This starter pack contains selected functions adapted from the lecture examples. It is **not a complete assignment solution**. You must integrate, adapt, validate, and extend the code.

## What is provided

- A validated shared `MusicalEvent` data model
- Pitch-name to frequency conversion
- Beat-to-second and beat-to-sample conversion
- A simple offline ADSR envelope
- Click-reducing fades and peak protection
- A reusable timeline and polyphonic mixer
- WAV export and optional playback
- A reference sine-wave voice for testing the pipeline
- Input-reader templates for ABC, MIDI, and MusicXML
- Synthesis strategy templates with TODO sections
- Basic tests for the common infrastructure

## What you must do

1. Choose one supplied symbolic input format: ABC, MIDI, or MusicXML.
2. Complete and validate the relevant input reader.
3. Convert the input into the shared event representation.
4. Select three synthesis techniques taught in the module.
5. Implement each technique in a separate module using the common interface.
6. Render the same melody with all three techniques.
7. Save three WAV files.
8. Conduct controlled parameter experiments.
9. Add one creative extension.
10. Complete the technical report template.

## Environment

Target: Python 3.14

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the reference pipeline

```bash
python -m src.main
```

The reference program uses a short hard-coded test event list and the sine-wave voice only to verify that timeline scheduling, mixing, playback, and WAV export work. Hard-coding the supplied assignment melody does **not** satisfy the assignment input requirement.

## Run tests

```bash
python -m unittest discover -s tests
```

## Important design rule

Parsing, event representation, synthesis, scheduling, mixing, analysis, and export should remain separate. Changing the synthesis technique should not require rewriting the parser or timeline.
