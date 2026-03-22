from .midi_note_mapper import MidiNoteMapper, Note
from .rhythm_analyzer import RhythmAnalyzer
from .symbol_manager import SymbolManager
from .notation_renderer import NotationRenderer


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

    # ---------------------------------------------------------
    # PREPOJENIE EXTERNÉHO RENDERERA (napr. grafického)
    # ---------------------------------------------------------
    def bind_renderer(self, renderer):
        """Pripojí externý renderer (grafický alebo iný)."""
        self.renderer = renderer

    # ---------------------------------------------------------
    # PRIDANIE AKORDU DO TIMELINE
    # ---------------------------------------------------------
    def add_chord(self, name: str, start_time: float):
        """
        Pridá akord do timeline a odošle ho rendereru.
        """
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
        """
        Pre mapovanie MIDI kanálov na stopy.
        CH0 = melody
        CH1 = bass
        CH9 = drums
        """
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
        """
        Spracuje jednu MIDI udalosť.

        Očakávaný tvar midi_event:
        {
            "type": "note_on" | "note_off",
            "note": int,
            "velocity": int,
            "time": float,
            "channel": int
        }
        """

        event_type = midi_event.get("type")
        pitch = midi_event.get("note")
        velocity = midi_event.get("velocity", 0)
        timestamp = midi_event.get("time", 0.0)
        channel = midi_event.get("channel", 0)

        # -----------------------------
        # NOTE ON
        # -----------------------------
        if event_type == "note_on" and velocity > 0:
            self.note_mapper.handle_note_on(
                pitch=pitch,
                velocity=velocity,
                channel=channel,
                timestamp=timestamp
            )
            return None

        # -----------------------------
        # NOTE OFF (alebo note_on s velocity 0)
        # -----------------------------
        if event_type in ("note_off", "note_on") and velocity == 0:
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

            # -----------------------------
            # Rhythm info
            # -----------------------------
            ppq = self.note_mapper.ppq
            beats = created_note.duration.ticks / ppq if ppq > 0 else 0.0
            rhythmic_name = self.rhythm_analyzer._quantize(beats)

            rhythm_info = {
                "beats": beats,
                "rhythm": rhythmic_name,
                "measure": created_note.position.measure,
                "beat_position": created_note.position.beat,
            }

            # -------------------------------------------------
            # BARLINE GENERÁCIA – nový takt = nová čiara
            # -------------------------------------------------
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

            # -----------------------------
            # SymbolManager
            # -----------------------------
            symbol = self.symbol_manager.get_symbol(
                note=created_note,
                rhythm=rhythmic_name
            )

            # -----------------------------
            # Timeline pre renderer
            # -----------------------------
            visual_duration = created_note.duration.ticks / 120.0

            timeline_item = {
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "color": symbol.get("color", "#FFFFFF"),
                "track_type": self._detect_track(channel),
            }

            self.timeline.append(timeline_item)

            # -----------------------------
            # Vykreslenie cez AKTUÁLNY renderer
            # -----------------------------
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
