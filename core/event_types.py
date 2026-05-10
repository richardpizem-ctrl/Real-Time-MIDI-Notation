# =========================================================
# Event Types v4.0.0-ready
# Centrálne definované typy udalostí pre celý projekt
# Pripravené pre AI, Real-Time Engine, Engraving Engine
# =========================================================

"""
Verzia 4.0.0-ready:

- AI eventy
- Real-time engine eventy
- Engraving engine eventy
- Editing system eventy
- Export pipeline eventy
- Performance monitoring
- System lifecycle eventy

Plne kompatibilné s EventBus v4 a AppController v4.
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

EXPORT_PDF = "export.pdf"
EXPORT_SVG = "export.svg"
EXPORT_MUSICXML = "export.musicxml"

# ---------------------------------------------------------
# SYSTEM EVENTS
# ---------------------------------------------------------
APP_STARTED = "system.app_started"
APP_STOPPED = "system.app_stopped"
SYSTEM_SHUTDOWN = "system.shutdown"
SYSTEM_REBOOT = "system.reboot"
SYSTEM_MODE_CHANGED = "system.mode_changed"

ERROR_OCCURRED = "system.error"
STATUS_MESSAGE = "system.status"

# ---------------------------------------------------------
# AI EVENTS (v4)
# ---------------------------------------------------------
AI_STARTED = "ai.started"
AI_STOPPED = "ai.stopped"
AI_EVENT = "ai.event"
AI_ERROR = "ai.error"
AI_SUGGESTION = "ai.suggestion"

# ---------------------------------------------------------
# REAL-TIME ENGINE EVENTS (v4)
# ---------------------------------------------------------
RT_STARTED = "rt.started"
RT_STOPPED = "rt.stopped"
RT_TICK = "rt.tick"
RT_LATENCY_WARNING = "rt.latency_warning"

# ---------------------------------------------------------
# ENGRAVING ENGINE EVENTS (v4)
# ---------------------------------------------------------
ENGRAVING_UPDATE = "engraving.update"
ENGRAVING_LAYOUT_CHANGED = "engraving.layout_changed"
ENGRAVING_COLLISION = "engraving.collision_detected"
ENGRAVING_REDRAW = "engraving.redraw"

# ---------------------------------------------------------
# EDITING SYSTEM EVENTS (v4)
# ---------------------------------------------------------
EDIT_MARKER_MOVED = "editing.marker_moved"
EDIT_RIPPLE = "editing.ripple"
EDIT_MODE_CHANGED = "editing.mode_changed"

# ---------------------------------------------------------
# PERFORMANCE MONITORING (v4)
# ---------------------------------------------------------
PERF_CPU = "perf.cpu"
PERF_RAM = "perf.ram"
PERF_FPS = "perf.fps"
PERF_EVENT_QUEUE = "perf.event_queue"
