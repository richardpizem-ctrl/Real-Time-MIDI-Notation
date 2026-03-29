from .midi_note_mapper import MidiNoteMapper, Note
from .rhythm_analyzer import RhythmAnalyzer
from .symbol_manager import SymbolManager
from .notation_renderer import NotationRenderer
from .key_detector import detect_key


class NotationProcessor:
    """
    Centrálna pipeline:
    MIDI → MidiNoteMapper → RhythmAnalyzer → SymbolManager → Renderer
    """

    def __init__(self):
        self.note_mapper = MidiNoteMapper()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.symbol_manager = SymbolManager()

        self.renderer = NotationRenderer()

        self.timeline: list[dict] = []
        self.current_chord = None

        self.last_measure: int | None = None

        self.active_pitches: set[int] = set()
        self.current_key: str | None = None

        self.last_note_by_pitch: dict[int, dict] = {}

        self.current_play_position: float = 0.0

        self.bpm: int = 120
        self.is_running: bool = False
        self.last_timestamp: float = 0.0

        self.track_colors = {
            "melody": (80, 160, 255),
            "bass": (120, 220, 120),
            "drums": (255, 150, 60),
            "chords": (255, 255, 120),
        }

    # ---------------------------------------------------------
    # PREPOJENIE EXTERNÉHO RENDERERA
    # ---------------------------------------------------------
    def bind_renderer(self, renderer):
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
    # FÁZA 3 – animačná slučka (60 FPS)
    # ---------------------------------------------------------
    def start_animation_loop(self):
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
    def update_play_position(self, timestamp: float):
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
    def _update_key(self, timestamp: float):
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
    def add_chord(self, name: str, start_time: float):
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

    def _get_track_color(self, track_type: str):
        return self.track_colors.get(track_type, (255, 120, 120))

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

            self._update_key(timestamp)

            try:
                self.note_mapper.handle_note_on(
                    pitch=pitch,
                    velocity=velocity,
                    channel=channel,
                    timestamp=timestamp
                )
            except Exception:
                pass

            return None

        # NOTE OFF
        if event_type in ("note_off", "note_on") and velocity == 0:
            if pitch in self.active_pitches:
                try:
                    self.active_pitches.remove(pitch)
                except Exception:
                    pass
                self._update_key(timestamp)

            created_note: Note | None = None

            def on_note_created(note: Note):
                nonlocal created_note
                created_note = note

            self.note_mapper.on_note_created = on_note_created
            try:
                self.note_mapper.handle_note_off(
                    pitch=pitch,
                    channel=channel,
                    timestamp=timestamp
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
                rhythmic_name = self.rhythm_analyzer._quantize(beats)
            except Exception:
                rhythmic_name = "unknown"

            rhythm_info = {
                "beats": beats,
                "rhythm": rhythmic_name,
                "measure": created_note.position.measure,
                "beat_position": created_note.position.beat,
            }

            current_measure = created_note.position.measure

            if self.last_measure is None:
                self.last_measure = current_measure

            if current_measure != self.last_measure:
                bar_item = {
                    "type": "barline",
                    "start": created_note.start_time,
                    "measure": current_measure
                }
                self.timeline.append(bar_item)

                if hasattr(self.renderer, "add_barline"):
                    try:
                        self.renderer.add_barline(bar_item["start"])
                    except Exception:
                        pass

                self.last_measure = current_measure

            try:
                symbol = self.symbol_manager.get_symbol(
                    note=created_note,
                    rhythm=rhythmic_name
                )
            except Exception:
                symbol = {}

            try:
                visual_duration = created_note.duration.ticks / 120.0
            except Exception:
                visual_duration = 0.0

            track_type = self._detect_track(channel)
            track_color = self._get_track_color(track_type)

            timeline_item = {
                "type": "note",
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "color": symbol.get("color", "#FFFFFF"),
                "track_type": track_type,
                "track_color": track_color,
            }

            self.timeline.append(timeline_item)

            prev_note = self.last_note_by_pitch.get(created_note.pitch)

            if prev_note:
                slur_item = {
                    "type": "slur",
                    "start_note": prev_note,
                    "end_note": {
                        "pitch": created_note.pitch,
                        "start": created_note.start_time,
                        "duration": visual_duration,
                        "track_type": track_type,
                        "track_color": track_color,
                    }
                }
                self.timeline.append(slur_item)

            self.last_note_by_pitch[created_note.pitch] = {
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "track_type": track_type,
                "track_color": track_color,
            }

            if self.renderer:
                if hasattr(self.renderer, "add_note"):
                    try:
                        self.renderer.add_note(timeline_item)
                    except Exception:
                        pass
                else:
                    if hasattr(self.renderer, "render"):
                        try:
                            self.renderer.render(self.timeline)
                        except Exception:
                            pass

            return {
                "note": created_note,
                "rhythm": rhythm_info,
                "symbol": symbol,
            }

        return None
