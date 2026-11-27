# Installation — recovery preview 4.3.1

## Windows

Use a fresh writable folder containing the entire repair branch. Python 3.10 is the locally
verified version; other environments are subject to CI and hardware checks.

1. Install Python 3.10+ if missing.
2. Double-click `PRIPRAVIT-MIDI.cmd`. Internet is needed to install the pinned packages in a local `.venv`.
3. Double-click `SPUSTIT-MIDI.cmd` and try **DEMO** first.
4. Connect a MIDI keyboard, press **Obnoviť**, select **Vstup >**, then **Pripojiť**.
5. Export recordings before closing. Export writes timestamped `.mid` files into `exports`.

The launcher does not use the BETA Python environment and does not replace the BETA application.
For sound, select a real MIDI output. Without it, playback is visual; no synthesizer is bundled.

## Command line / development

```text
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -B main.py --demo
.venv\Scripts\python.exe -B -m pytest -q
```

On Linux use `.venv/bin/python`; Linux is a CI target, not a locally verified hardware platform.
`python main.py --headless --demo --frames 120` performs a bounded display-less startup test.
All launchers and their status are listed in [LAUNCHERS.md](LAUNCHERS.md).

## Troubleshooting

- **Missing dependency:** prepare the local environment with the preparation script.
- **Bad config.json:** run diagnostics, then explicitly invoke `OPRAVIT-NASTAVENIA.cmd` if recovery is appropriate.
- **Missing/broken source:** use a known-good complete copy. Diagnostics will report it; recovery will not invent code.
- **Device unavailable/occupied:** verify the exact input name and whether another program holds the port.
- **No sound:** choose an external MIDI output and check its instrument. The UI alone does not synthesize audio.

Do not submit recordings, secrets or personal device details without reviewing them first.
Hardware operation remains an acceptance task; a simulated port test does not establish it.
