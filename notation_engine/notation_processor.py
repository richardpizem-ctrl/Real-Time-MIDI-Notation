from .midi_note_mapper import MidiNoteMapper, Note
from .rhythm_analyzer import RhythmAnalyzer
from .symbol_manager import SymbolManager
from .notation_renderer import NotationRenderer


class NotationProcessor:
    """
    Centrálna pipeline:
    MIDI → MidiNoteMapper → RhythmAnalyzer → SymbolManager → NotationRenderer
    """

    def __init__(self):
        self.note_mapper = MidiNoteMapper()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.symbol_manager = SymbolManager()
        self.renderer = NotationRenderer()

        # Timeline pre renderer (zoznam dictov)
        self.timeline = []
        self.current_chord = None  # ak budeš neskôr posielať aj akordy

    def process_midi_event(self, midi_event: dict):
        """
        Spracuje jednu MIDI udalosť.

        Očakávaný tvar midi_event:
        {
            "type": "note_on" | "note_off",
            "note": int,          # MIDI pitch
            "velocity": int,
            "time": float,        # sekundy
            "channel": int
        }
        """

        event_type = midi_event.get("type")
        pitch = midi_event.get("note")
        velocity = midi_event.get("velocity", 0)
        timestamp = midi_event.get("time", 0.0)
        channel = midi_event.get("channel", 0)

        # -----------------------------
        # NOTE ON (začiatok noty)
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
        # NOTE OFF (koniec noty)
        # alebo NOTE ON s velocity 0
        # -----------------------------
        if event_type in ("note_off", "note_on") and velocity == 0:
            created_note: Note | None = None

            def on_note_created(note: Note):
                nonlocal created_note
                created_note = note

            # nastavíme callback a spracujeme note_off
            self.note_mapper.on_note_created = on_note_created
            self.note_mapper.handle_note_off(
                pitch=pitch,
                channel=channel,
                timestamp=timestamp
            )

            # ak sa nota nevytvorila, nemáme čo ďalej spracovať
            if created_note is None:
                return None

            # -----------------------------
            # Rhythm "info" – odvodené z duration
            # -----------------------------
            # duration v tickoch → beaty
            ppq = self.note_mapper.ppq
            beats = created_note.duration.ticks / ppq if ppq > 0 else 0.0

            # použijeme kvantizáciu z RhythmAnalyzer (aj keď je interná)
            rhythmic_name = self.rhythm_analyzer._quantize(beats)

            rhythm_info = {
                "beats": beats,
                "rhythm": rhythmic_name,
                "measure": created_note.position.measure,
                "beat_position": created_note.position.beat,
            }

            # -----------------------------
            # SymbolManager – vytvorenie symbolu
            # -----------------------------
            # Predpoklad: SymbolManager vie pracovať s Note + rytmickým názvom
            symbol = self.symbol_manager.get_symbol(
                note=created_note,
                rhythm=rhythmic_name
            )

            # -----------------------------
            # Pridanie do timeline pre renderer
            # -----------------------------
            # start_time v sekundách → X pozícia (len jednoduché škálovanie)
            visual_duration = created_note.duration.ticks / 120.0  # 1/16 grid, podľa kvantizácie
            timeline_item = {
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "color": symbol.get("color", "#FFFFFF"),
            }

            self.timeline.append(timeline_item)

            # -----------------------------
            # Vykreslenie
            # -----------------------------
            self.renderer.render(self.timeline, current_chord=self.current_chord)

            return {
                "note": created_note,
                "rhythm": rhythm_info,
                "symbol": symbol,
            }

        # iné typy udalostí zatiaľ ignorujeme
        return None
