# =========================================================
# Event Types v4.1.0
# Centrálne definované typy udalostí pre Runtime 4.x–5.x
# Stabilná CORE verzia bez AI/RT/Engraving eventov
# =========================================================

"""
Verzia 4.1.0:

- stabilné systémové eventy
- MIDI eventy
- track eventy
- recording eventy
- export eventy
- system lifecycle eventy

Pripravené pre:
- AppController v4.1.0
- EventBus v4.1.0
- Runtime 5.x (KG, Envoy, System Agent)
"""

# ---------------------------------------------------------
# MIDI EVENTS
# ---------------------------------------------------------
MIDI_NOTE_ON = "midi.note_on"
MIDI_NOTE_OFF = "midi.note_off"
MIDI_CONTROL_CHANGE = "midi.cc"

# ---------------------------------------------------------
# TRACK EVENTS
# ---------------------------------------------------------
TRACK_SELECTED = "track.selected"
TRACK_NAME_CHANGED = "track.name_changed"
TRACK_COLOR_CHANGED = "track.color_changed"
TRACK_MUTED = "track.muted"
TRACK_SOLOED = "track.soloed"

# ---------------------------------------------------------
# RECORDING EVENTS
# ---------------------------------------------------------
NOTE_RECORDED = "recording.note_recorded"
RECORDING_STARTED = "recording.started"
RECORDING_STOPPED = "recording.stopped"

# ---------------------------------------------------------
# EXPORT EVENTS
# ---------------------------------------------------------
MIDI_EXPORT_REQUEST = "export.midi_request"
MIDI_EXPORTED = "export.midi_done"

# ---------------------------------------------------------
# SYSTEM EVENTS
# ---------------------------------------------------------
APP_STARTED = "system.app_started"
APP_STOPPED = "system.app_stopped"
SYSTEM_SHUTDOWN = "system.shutdown"

ERROR_OCCURRED = "system.error"
STATUS_MESSAGE = "system.status"
