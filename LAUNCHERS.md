# Supported launchers

| File | Purpose after this repair |
| --- | --- |
| `SPUSTIT-MIDI.cmd` | Recommended Windows application start using local `.venv`. |
| `main.py` | Single implementation of command-line start and preflight diagnostics. |
| `run.py` | Compatibility alias to `main.py`, with the same arguments. |
| `preview.py` | Demo alias to the same application; adds `--demo`. No separate Tk renderer loop. |
| `ui/window.py` | Compatibility window/launcher using the same Pygame application. |
| `PRIPRAVIT-MIDI.cmd` | Prepare dependencies, not an application window. |
| `DIAGNOSTIKA.cmd` | Read-only diagnostic report, not a second application. |
| `OPRAVIT-NASTAVENIA.cmd` | Explicit, backed-up settings recovery only. |
| `setup.py` | Packaging compatibility, not an application launcher. |
| `test_chords.py` / `tests/` | Demonstrations and tests, not the full application. |

The old `run.py`, `preview.py` and `ui/window.py` routes had divergent or broken dependencies.
They have been redirected, rather than leaving multiple misleading startup instructions.
All four Python application entry points share the same diagnostics and are covered by tests.
Importing a core package must not start a window or worker.
