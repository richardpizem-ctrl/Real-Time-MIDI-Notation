# SIRIUS — Real-Time MIDI Notation

**Recovery preview 4.3.1 · Python · Local MIDI recording and visualisation**

This pull request repairs a previously unverified source tree. It provides one supported
application path with automated tests. It is not yet a hardware-validated release.

![SIRIUS](SIRIUS%20PROGRAM%20S%20EM.png)

## Start on Windows

1. Extract or clone the complete **repair branch** into a writable folder.
2. Install Python 3.10+; Python 3.10 is the locally tested environment.
3. Run **PRIPRAVIT-MIDI.cmd** once. It prepares a local `.venv` and installs dependencies.
4. Run **SPUSTIT-MIDI.cmd**. Click **DEMO** to try a simulated two-channel phrase without hardware.
5. To use a keyboard, connect it, refresh devices, select the input and click **Pripojiť**.

See [installation](INSTALLATION.md) and the Slovak [quick-start text](PRECITAJ-MA.txt).
Without a selected MIDI output, playback is visual. There is no built-in synthesizer.

## Supported and tested software path

- One application through `main.py`, `run.py`, `preview.py` and the compatibility window.
- 16-channel recording, note-on/off, sustain, retriggers and disconnect cleanup.
- Basic staff preview with note names, piano-roll history and keyboard display.
- MIDI import/export retaining timing, channels, controllers and pitch bend.
- Visual playback with optional external MIDI output, pause/resume and track mute.
- Basic chord/key estimates. Estimates are not verdicts that a musician played incorrectly.
- Read-only startup diagnostics and explicit recovery of invalid/missing settings with backup.

This is a basic notation preview, not a complete professional engraving system. Historical
rendering/editing experiments retained in the tree are not all connected to the supported UI.
There is no audio intonation/level analyzer or SIRIUS BETA bridge yet.

## Verification and remaining acceptance

The local Windows/Python 3.10 suite has **96 passing tests**, including simulated input,
recording, timed MIDI round trips, tempo changes, all 12 key transpositions, playback,
8,000 queued MIDI events, launchers, read-only diagnostics and failed-write recovery.
Normal Windows SDL startup/shutdown and dummy-display rendering were checked. A prior
75-test recovery ZIP was also installed and tested after extraction; the PR adds launcher
and settings diagnostics coverage. GitHub Actions checks Windows/Linux and Python 3.10/3.12;
its results must be read separately from local results.

**Still required:** a real MIDI keyboard/driver, actual MIDI sound output, reconnection and
manual UI acceptance. The PR remains draft until this acceptance is complete. No zero-latency,
universal hardware compatibility, world-first or full-module validation claim is made.

## Diagnostics and controlled recovery

- `DIAGNOSTIKA.cmd` reports missing libraries, missing/broken critical source files and settings.
- `OPRAVIT-NASTAVENIA.cmd` restores defaults only for missing/invalid `config.json`.
- A damaged configuration is backed up byte-for-byte in `recovery-backups` before replacement.
- Valid custom settings remain unchanged. A failed replacement preserves the original.
- No source code or recording is rewritten, and no dependency is installed by recovery.

This is limited settings recovery, **not autonomous self-repair of the application**.
Missing libraries require the preparation step; missing code requires a known-good source copy.

## Documentation

[Installation](INSTALLATION.md) · [Verification and repair scope](REPAIR_STATUS.md) ·
[Launcher map](LAUNCHERS.md) · [Module map](MODULE_MAP.md) · [Roadmap](ROADMAP.md) ·
[Contributing](CONTRIBUTING.md) · [License](LICENSE)
