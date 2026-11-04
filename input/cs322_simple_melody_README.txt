CS322 SIMPLE SYMBOLIC MELODY
================================

The three files contain the same musical material.

Global settings
---------------
Time signature: 4/4
Tempo: 100 quarter-note beats per minute
Key signature: C major / no sharps or flats
Total length: 8 quarter-note beats (2 measures)

Musical events in quarter-note units
------------------------------------
C4: onset 0, duration 1
D4: onset 1, duration 1
E4: onset 2, duration 1
F4: onset 3, duration 1
C4 + E4 + G4 chord: onset 4, duration 1
Rest: onset 5, duration 1
G4: onset 6, duration 2

Files
-----
cs322_simple_melody.abc       ABC notation
cs322_simple_melody.mid       Standard MIDI File, 480 ticks per quarter note
cs322_simple_melody.musicxml  MusicXML 4.0 partwise score

Teaching notes
--------------
- The ABC and MusicXML files explicitly encode the rest.
- The MIDI file represents the rest as a gap with no active notes.
- The chord is represented by simultaneous notes in all three formats.
- The input formats do not provide identical detail. Students should use and
  document assignment defaults for missing dynamic or articulation values.
