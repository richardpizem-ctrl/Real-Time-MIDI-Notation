from .midi_note_mapper import MidiNoteMapper, Note
from .rhythm_analyzer import RhythmAnalyzer
from .symbol_manager import SymbolManager
from .notation_renderer import NotationRenderer
from .key_detector import detect_key
from .harmony_engine import HarmonyEngine
from .chord_detector import detect_chord


class NotationProcessor:
    """
    Centrálna pipeline:
    MIDI → MidiNoteMapper → RhythmAnalyzer → SymbolManager → Renderer
    """

    def __init__(self, track_system, event_bus):
        self.track_system = track_system
        self.event_bus = event_bus

        self.note_mapper = MidiNoteMapper()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.symbol_manager = SymbolManager()

        self.renderer = NotationRenderer()

        self.timeline: list[dict] = []
        self.current_chord = None

        self.last_measure: int | None = None

        self.active_pitches: set[int] = set()
        self.current_key: str | None = None

        self.current_play_position: float = 0.0

        self.bpm: int = 120
        self.is_running: bool = False
        self.last_timestamp: float = 0.0

        self.staff_ui = None
        self.piano_ui = None
        self.visualizer_ui = None

        self.harmony = HarmonyEngine()

    # ---------------------------------------------------------
    # PREPOJENIE UI KOMPONENTOV
    # ---------------------------------------------------------
    def bind_staff(self, ui) -> None:
        self.staff_ui = ui

    def bind_piano(self, ui) -> None:
        self.piano_ui = ui

    def bind_visualizer(self, ui) -> None:
        self.visualizer_ui = ui

    # ---------------------------------------------------------
    # PREPOJENIE EXTERNÉHO RENDERERA
    # ---------------------------------------------------------
    def bind_renderer(self, renderer) -> None:
        self.renderer = renderer

    # ---------------------------------------------------------
    # FÁZA 3 – prepočet delta času
    # ---------------------------------------------------------
    def _compute_time_delta(self, timestamp: float) -> float:
        try:
            dt = float(timestamp) - float(self.last_timestamp)
        except Exception:
            dt = 0.0
        if dt < 0:
            dt = 0.0
        self.last_timestamp = float(timestamp)
        return dt

    # ---------------------------------------------------------
    # FÁZA 3 – animačná slučka
    # ---------------------------------------------------------
    def start_animation_loop(self) -> None:
        if not hasattr(self.renderer, "tick"):
            return
        if self.is_running:
            return

        self.is_running = True

        import threading
        import time

        def loop():
            while self.is_running:
                time.sleep(0.016)
                try:
                    self.renderer.tick(0.016)
                except Exception:
                    pass

        threading.Thread(target=loop, daemon=True).start()

    # ---------------------------------------------------------
    # UPDATE PLAY POSITION
    # ---------------------------------------------------------
    def update_play_position(self, timestamp: float) -> None:
        try:
            self.current_play_position = float(timestamp)
        except Exception:
            self.current_play_position = 0.0

        if hasattr(self.renderer, "set_playhead"):
            try:
                self.renderer.set_playhead(self.current_play_position)
            except Exception:
                pass

    # ---------------------------------------------------------
    # KEY DETECTION UPDATE
    # ---------------------------------------------------------
    def _update_key(self, timestamp: float) -> None:
        if not self.active_pitches:
            return

        try:
            new_key = detect_key(self.active_pitches)
        except Exception:
            new_key = None

        if new_key and new_key != self.current_key:
            self.current_key = new_key

            key_item = {
                "type": "key_change",
                "key": new_key,
                "start": timestamp,
            }

            self.timeline.append(key_item)

            if hasattr(self.renderer, "add_key_change"):
                try:
                    self.renderer.add_key_change(key_item)
                except Exception:
                    pass

    # ---------------------------------------------------------
    # PRIDANIE AKORDU DO TIMELINE
    # ---------------------------------------------------------
    def add_chord(self, name: str, start_time: float) -> dict:
        chord_item = {
            "type": "chord",
            "name": name,
            "start": start_time,
            "track_type": "chords",
        }

        self.timeline.append(chord_item)

        if hasattr(self.renderer, "add_chord"):
            try:
                self.renderer.add_chord(chord_item)
            except Exception:
                pass

        return chord_item

    # ---------------------------------------------------------
    # MAPOVANIE MIDI KANÁLOV NA STOPY
    # ---------------------------------------------------------
    def _detect_track(self, channel: int) -> str:
        try:
            ch = int(channel)
        except Exception:
            ch = 0

        if ch == 0:
            return "melody"
        if ch == 1:
            return "bass"
        if ch == 9:
            return "drums"
        return "melody"

    # ---------------------------------------------------------
    # EXTRAKCIA ROOTU Z NÁZVU AKORDU
    # ---------------------------------------------------------
    def _extract_root_from_chord_name(self, chord_name: str):
        if not chord_name or not isinstance(chord_name, str):
            return None

        root = chord_name[0]
        if len(chord_name) > 1 and chord_name[1] in ("#", "b"):
            root = chord_name[:2]

        pitch_map = {
            "C": 0, "C#": 1, "Db": 1,
            "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6,
            "G": 7, "G#": 8, "Ab": 8,
            "A": 9, "A#": 10, "Bb": 10,
            "B": 11,
        }
        return pitch_map.get(root, None)

    # ---------------------------------------------------------
    # HLAVNÁ FUNKCIA – spracovanie MIDI udalosti
    # ---------------------------------------------------------
    def process_midi_event(self, midi_event: dict):
        if not isinstance(midi_event, dict):
            return None

        event_type = midi_event.get("type")
        pitch = midi_event.get("note")
        velocity = midi_event.get("velocity", 0)
        timestamp = midi_event.get("time", 0.0)
        channel = midi_event.get("channel", 0)

        if pitch is None:
            return None

        try:
            velocity = int(velocity)
        except Exception:
            velocity = 0

        if not self.is_running:
            self.start_animation_loop()

        self.update_play_position(timestamp)

        # NOTE ON
        if event_type == "note_on" and velocity > 0:
            try:
                self.active_pitches.add(int(pitch))
            except Exception:
                pass

            try:
                detected = detect_chord(self.active_pitches)
            except Exception:
                detected = None
            self.current_chord = detected

            self._update_key(timestamp)

            if self.staff_ui and hasattr(self.staff_ui, "highlight_note"):
                try:
                    self.staff_ui.highlight_note(pitch)
                except Exception:
                    pass

            if self.piano_ui and hasattr(self.piano_ui, "highlight_key"):
                try:
                    self.piano_ui.highlight_key(pitch)
                except Exception:
                    pass

            if self.visualizer_ui and hasattr(self.visualizer_ui, "show_note"):
                try:
                    self.visualizer_ui.show_note(pitch)
                except Exception:
                    pass

            try:
                self.note_mapper.handle_note_on(
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                    timestamp=timestamp,
                )
            except Exception:
                pass

            return None

        # NOTE OFF (alebo note_on s velocity 0)
        if event_type in ("note_off", "note_on") and velocity == 0:
            if pitch in self.active_pitches:
                try:
                    self.active_pitches.remove(pitch)
                except Exception:
                    pass

                try:
                    detected = detect_chord(self.active_pitches)
                except Exception:
                    detected = None
                self.current_chord = detected

                self._update_key(timestamp)

            if self.piano_ui and hasattr(self.piano_ui, "unhighlight_key"):
                try:
                    self.piano_ui.unhighlight_key(pitch)
                except Exception:
                    pass

            if self.staff_ui:
                try:
                    if hasattr(self.staff_ui, "clear_highlight"):
                        self.staff_ui.clear_highlight(pitch)
                    elif hasattr(self.staff_ui, "unhighlight_note"):
                        self.staff_ui.unhighlight_note(pitch)
                except Exception:
                    pass

            created_note: Note | None = None

            def on_note_created(note: Note):
                nonlocal created_note
                created_note = note

            self.note_mapper.on_note_created = on_note_created
            try:
                self.note_mapper.handle_note_off(
                    pitch=pitch,
                    channel=channel,
                    timestamp=timestamp,
                )
            except Exception:
                return None

            if created_note is None:
                return None

            ppq = getattr(self.note_mapper, "ppq", 0)
            try:
                beats = created_note.duration.ticks / ppq if ppq > 0 else 0.0
            except Exception:
                beats = 0.0

            try:
                rhythmic_name = self.rhythm_analyzer._quantize(beats
