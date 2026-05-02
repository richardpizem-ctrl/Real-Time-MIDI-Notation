# =========================================================
# Event Types v2.0.0
# Centrálne definované typy udalostí pre celý projekt
# Stabilné, konzistentné, bezpečné API pre EventBus
# =========================================================

"""
Centrálne definované typy udalostí pre celý projekt.

Stabilizované (v2.0.0):
- jednotná štruktúra názvov
- žiadne duplicity
- bezpečné, konzistentné názvy
- pripravené pre EventBus, UIManager, TrackSystem, NotationProcessor
- kompatibilné s real-time spracovaním
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
ERROR_OCCURRED = "system.error"
STATUS_MESSAGE = "system.status"
