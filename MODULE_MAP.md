# Supported module map — recovery preview 4.3.1

| Module | Supported responsibility |
| --- | --- |
| `main.py` | Arguments, startup diagnostics, settings load, single application start. |
| `core/diagnostics.py` | Read-only checks and explicit atomic settings replacement after backup. |
| `core/app_controller.py` | Queue, event routing and main-thread recording ownership. |
| `midi_input/message_parser.py` | Canonical Mido normalization; live time is monotonic seconds. |
| `midi_input/midi_listener.py` | Reader worker, device opening, error reporting and shutdown. |
| `midi_input/event_router.py` | Consistent routing to note/control subscribers. |
| `core/track_system.py` | 16-channel recording, held/sustained notes and cleanup. |
| `core/track_manager.py` | Mute/solo, channel transforms and track controls. |
| `core/notation_processor.py` | Timed MIDI file I/O and tempo-aware import. |
| `core/playback_engine.py` | Single-thread scheduling, external output, pause/resume and cleanup. |
| `notation_engine/chord_detector.py`, `key_detector.py` | Basic musical estimates, not general error verdicts. |
| `ui/application.py`, `ui/timeline_ui.py`, `ui/PianoUI.py` | Supported Pygame window and previews. |
| `core/editing/` | Tested primitives; not a fully integrated graphical score editor. |

Other rendering, AI and UI files are retained historical experiments. Their presence does not
establish that they are usable together. They are excluded from the documented startup path.
No BETA bridge or audio analysis module has been implemented in this repair.
