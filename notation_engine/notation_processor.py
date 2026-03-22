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

        # defaultný renderer (textový)
        self.renderer = NotationRenderer()

        # Timeline pre renderer (zoznam dictov)
        self.timeline = []
        self.current_chord = None

        # posledný takt pre barline generáciu
        self.last_measure = None

        # KEY DETECTION
        self.active_pitches = set()
        self.current_key = None

    # ---------------------------------------------------------
    # PREPOJENIE EXTERNÉHO RENDERERA (napr. grafického)
    # ---------------------------------------------------------
    def bind_renderer(self, renderer):
        """Pripojí externý renderer (grafický alebo iný)."""
        self.renderer = renderer

    # ---------------------------------------------------------
    # KEY DETECTION UPDATE
    # ---------------------------------------------------------
    def _update_key(self, timestamp: float):
        if not self.active_pitches:
            return

        new_key = detect_key(self.active_pitches)
        if new_key and new_key != self.current_key:
            self.current_key = new_key

            key_item = {
                "type": "key_change",
                "key": new_key,
                "start": timestamp,
            }

            self.timeline.append(key_item)

            if hasattr(self.renderer, "add_key_change"):
                self.renderer.add_key_change(key_item)

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
            self.renderer.add_chord(chord_item)

        return chord_item

    # ---------------------------------------------------------
    # MAPOVANIE MIDI KANÁLOV NA STOPY
    # ---------------------------------------------------------
    def _detect_track(self, channel: int) -> str:
        if channel == 0:
            return "melody"
        if channel == 1:
            return "bass"
        if channel == 9:
            return "drums"
        return "melody"

    # ---------------------------------------------------------
    # HLAVNÁ FUNKCIA – spracovanie MIDI udalosti
    # ---------------------------------------------------------
    def process_midi_event(self, midi_event: dict):
        event_type = midi_event.get("type")
        pitch = midi_event.get("note")
        velocity = midi_event.get("velocity", 0)
        timestamp = midi_event.get("time", 0.0)
        channel = midi_event.get("channel", 0)

        # -----------------------------
        # NOTE ON
        # -----------------------------
        if event_type == "note_on" and velocity > 0:
            self.active_pitches.add(pitch)
            self._update_key(timestamp)

            self.note_mapper.handle_note_on(
                pitch=pitch,
                velocity=velocity,
                channel=channel,
                timestamp=timestamp
            )
            return None

        # -----------------------------
        # NOTE OFF
        # -----------------------------
        if event_type in ("note_off", "note_on") and velocity == 0:
            if pitch in self.active_pitches:
                self.active_pitches.remove(pitch)
                self._update_key(timestamp)

            created_note: Note | None = None

            def on_note_created(note: Note):
                nonlocal created_note
                created_note = note

            self.note_mapper.on_note_created = on_note_created
            self.note_mapper.handle_note_off(
                pitch=pitch,
                channel=channel,
                timestamp=timestamp
            )

            if created_note is None:
                return None

            # Rhythm info
            ppq = self.note_mapper.ppq
            beats = created_note.duration.ticks / ppq if ppq > 0 else 0.0
            rhythmic_name = self.rhythm_analyzer._quantize(beats)

            rhythm_info = {
                "beats": beats,
                "rhythm": rhythmic_name,
                "measure": created_note.position.measure,
                "beat_position": created_note.position.beat,
            }

            # BARLINE
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
                    self.renderer.add_barline(bar_item["start"])

                self.last_measure = current_measure

            # SymbolManager
            symbol = self.symbol_manager.get_symbol(
                note=created_note,
                rhythm=rhythmic_name
            )

            # Timeline
            visual_duration = created_note.duration.ticks / 120.0

            timeline_item = {
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "color": symbol.get("color", "#FFFFFF"),
                "track_type": self._detect_track(channel),
            }

            self.timeline.append(timeline_item)

            # Renderer
            if self.renderer:
                if hasattr(self.renderer, "add_note"):
                    self.renderer.add_note(timeline_item)
                else:
                    self.renderer.render(self.timeline)

            return {
                "note": created_note,
                "rhythm": rhythm_info,
                "symbol": symbol,
            }

        return None
