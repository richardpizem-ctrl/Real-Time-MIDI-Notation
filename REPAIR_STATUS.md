# Recovery preview 4.3.1 — 27 November 2026

Local working repair based on upstream commit `89eededd3478b31c145c1ac66bb5e7b60773143f`.
This is proposed through a draft GitHub PR; it has not been merged into the default branch or into BETA.

## Baseline failures

The original test collection stopped with eight import errors. The sources had a circular
`core`/configuration import, missing classes/modules in package initializers, a parser file
containing a router instead of MessageParser, mismatched entry-point constructor calls,
invalid Python in `setup.py` and `ui/timeline_ui.py`, and exports with zero event deltas.
Key profiles were rotated in the wrong direction, producing transposed key errors.

## Supported path after repair

`SPUSTIT-MIDI.cmd` -> `main.py` (also `run.py`) -> AppController -> MIDIListener -> bounded
queue -> main-thread EventRouter -> TrackSystem -> analysis / Pygame UI / timed MIDI I/O.

- Separate preparation of `.venv` and pinned runtime dependencies.
- 16-channel note capture, velocity-zero note-off, sustain, channel controls, pitch bend,
  retrigger handling and closure of notes on input stop/disconnect.
- Basic staff preview with note names, piano-roll history and reused PianoUI keyboard.
- Device list/selection, simulation demo, import/export, recording counts and track mute.
- Chord/key estimates; corrected key-profile rotation tested in all 12 roots.
- MIDI import respects tempo changes. Export preserves seconds as delta ticks, channel and
  controls, closes active notes in a copy and does not stop the live session.
- Visual playback and optional external MIDI output, pause/resume and note cleanup.
- Errors are shown in the interface instead of silently abandoning main-loop initialization.
- Existing selection, region, ghost and snapping primitive tests are retained.

## Verification

96 pytest cases passed on Windows / Python 3.10, with pygame 2.6.1, mido 1.3.3,
python-rtmidi 1.5.8 and pytest 8.3.5. Baseline/test logs are retained outside the package
in the Codex outputs folder. Demonstration functions called `test_chord(notes)` were
renamed so pytest no longer treats their sample arguments as missing fixtures; new
assertion-based tests verify major/minor triads. A floating-point test uses approximate
comparison instead of requiring bit-exact decimal equality.

Coverage includes simulated reader ports, main-thread recording, channel separation,
sustain, repeat notes, note cleanup, missing and disconnected devices, queue overflow,
8,000 MIDI events, timed import/export/reload, tempo changes, invalid-file preservation,
playback scheduling, pause/resume, all 12 major/minor triads and major key transpositions,
and actual Pygame rendering using the SDL dummy display.

`main.py --headless --demo --frames 120` started and exited cleanly. A rendered image
was inspected. The normal Windows SDL window also started and exited through the regular launcher in a fresh extracted copy. Mouse/device interaction and an actual instrument remain unverified. Editable packaging was
built and installed in the test environment after a temporary-directory workaround for
the host environment's braces in its TEMP path; no global Python installation was changed.

## Remaining scope

A physical keyboard/driver, device reconnection in real Windows hardware, actual MIDI sound
output and native desktop interaction need live verification. No built-in synthesizer,
audio pitch/level measurement, general music-inspector verdicts or BETA bridge is claimed.
The basic staff preview is not a complete engraving system (ties, beams, accidental spelling,
MusicXML and score layout are not validated). Imported tempo changes preserve event timing;
export uses the selected constant tempo to represent that timing.

The repository also retains earlier disconnected UI/rendering/notation experiments.
They are not loaded by the supported entry point and are not all repaired or covered by
these tests. Do not advertise every historical README feature as implemented.
The source archive is a recovery preview for testing, not an official new public release.

## PR follow-up

The PR also redirects `preview.py` and `ui/window.py` to the supported application.
Startup diagnostics check libraries, source syntax and settings. Explicit settings recovery
backs up exact invalid bytes and atomically restores validated defaults; source/recordings
are outside scope. Tests cover read-only diagnostics, valid-setting preservation, missing
libraries, malformed/out-of-range settings, failed replacement and launcher consistency.
CI is configured for Windows/Linux and Python 3.10/3.12; results are not assumed in advance.
