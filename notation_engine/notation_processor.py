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
        self.timeline: list[dict] = []
        self.current_chord = None

        # posledný takt pre barline generáciu
        self.last_measure: int | None = None

        # KEY DETECTION
        self.active_pitches: set[int] = set()
        self.current_key: str | None = None

        # 🔥 FÁZA 2 – aktuálna pozícia prehrávania
        self.current_play_position: float = 0.0

        # 🔥 FÁZA 3 – animácia prehrávania
        self.bpm: int = 120
        self.is_running: bool = False
        self.last_timestamp: float = 0.0

        # UI komponenty (doplníme cez bind)
        self.staff_ui = None
        self.piano_ui = None
        self.visualizer_ui = None

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
    # PREPOJENIE EXTERNÉHO RENDERERA (napr. grafického)
    # ---------------------------------------------------------
    def bind_renderer(self, renderer) -> None:
        """Pripojí externý renderer (grafický alebo iný)."""
        self.renderer = renderer

    # ---------------------------------------------------------
    # FÁZA 3 – prepočet delta času
    # ---------------------------------------------------------
    def _compute_time_delta(self, timestamp: float) -> float:
        dt = timestamp - self.last_timestamp
        if dt < 0:
            dt = 0.0
        self.last_timestamp = timestamp
        return dt

    # ---------------------------------------------------------
    # FÁZA 3 – animačná slučka
    # ---------------------------------------------------------
    def start_animation_loop(self) -> None:
        """Spustí plynulú animáciu playheadu (60 FPS), ak renderer podporuje tick()."""
        if not hasattr(self.renderer, "tick"):
            return

        if self.is_running:
            return

        self.is_running = True

        import threading
        import time

        def loop():
            while self.is_running:
                time.sleep(0.016)  # ~60 FPS
                self.renderer.tick(0.016)

        threading.Thread(target=loop, daemon=True).start()

    # ---------------------------------------------------------
    # UPDATE PLAY POSITION  🔥 FÁZA 2
    # ---------------------------------------------------------
    def update_play_position(self, timestamp: float) -> None:
        """Aktualizuje aktuálnu pozíciu prehrávania a odošle ju rendereru."""
        self.current_play_position = timestamp

        if hasattr(self.renderer, "set_playhead"):
            self.renderer.set_playhead(timestamp)

    # ---------------------------------------------------------
    # KEY DETECTION UPDATE
    # ---------------------------------------------------------
    def _update_key(self, timestamp: float) -> None:
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
    def add_chord(self, name: str, start_time: float) -> dict:
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

        if pitch is None:
            return None

        # 🔥 FÁZA 3 – spustenie animácie pri prvom evente
        if not self.is_running:
            self.start_animation_loop()

        # 🔥 FÁZA 2 – aktualizácia pozície prehrávania
        self.update_play_position(timestamp)

        # NOTE ON
        if event_type == "note_on" and velocity > 0:
            self.active_pitches.add(pitch)
            self._update_key(timestamp)

            if self.staff_ui and hasattr(self.staff_ui, "highlight_note"):
                self.staff_ui.highlight_note(pitch)

            if self.piano_ui and hasattr(self.piano_ui, "highlight_key"):
                self.piano_ui.highlight_key(pitch)

            if self.visualizer_ui and hasattr(self.visualizer_ui, "show_note"):
                self.visualizer_ui.show_note(pitch)

            self.note_mapper.handle_note_on(
                pitch=pitch,
                velocity=velocity,
                channel=channel,
                timestamp=timestamp,
            )
            return None

        # NOTE OFF (alebo note_on s velocity 0)
        if event_type in ("note_off", "note_on") and velocity == 0:
            if pitch in self.active_pitches:
                self.active_pitches.remove(pitch)
                self._update_key(timestamp)

            if self.piano_ui and hasattr(self.piano_ui, "unhighlight_key"):
                self.piano_ui.unhighlight_key(pitch)

            if self.staff_ui:
                # podpora rôznych API názvov
                if hasattr(self.staff_ui, "clear_highlight"):
                    self.staff_ui.clear_highlight(pitch)
                elif hasattr(self.staff_ui, "unhighlight_note"):
                    self.staff_ui.unhighlight_note(pitch)

            created_note: Note | None = None

            def on_note_created(note: Note):
                nonlocal created_note
                created_note = note

            self.note_mapper.on_note_created = on_note_created
            self.note_mapper.handle_note_off(
                pitch=pitch,
                channel=channel,
                timestamp=timestamp,
            )

            if created_note is None:
                return None

            ppq = self.note_mapper.ppq
            beats = created_note.duration.ticks / ppq if ppq > 0 else 0.0
            rhythmic_name = self.rhythm_analyzer._quantize(beats)

            rhythm_info = {
                "beats": beats,
                "rhythm": rhythmic_name,
                "measure": created_note.position.measure,
                "beat_position": created_note.position.beat,
            }

            current_measure = created_note.position.measure

            # taktové čiary
            if self.last_measure is None:
                self.last_measure = current_measure

            if current_measure != self.last_measure:
                bar_item = {
                    "type": "barline",
                    "start": created_note.start_time,
                    "measure": current_measure,
                }
                self.timeline.append(bar_item)

                if hasattr(self.renderer, "add_barline"):
                    # renderer si môže premapovať čas → x pozíciu
                    self.renderer.add_barline(bar_item["start"])

                self.last_measure = current_measure

            symbol = self.symbol_manager.get_symbol(
                note=created_note,
                rhythm=rhythmic_name,
            )

            # vizuálna dĺžka – zatiaľ jednoduchý prepočet
            visual_duration = created_note.duration.ticks / 120.0

            timeline_item = {
                "pitch": created_note.pitch,
                "start": created_note.start_time,
                "duration": visual_duration,
                "color": symbol.get("color", "#FFFFFF"),
                "track_type": self._detect_track(channel),
            }

            self.timeline.append(timeline_item)

            if self.renderer:
                if hasattr(self.renderer, "add_note"):
                    self.renderer.add_note(timeline_item)
                else:
                    # fallback – ak renderer nemá add_note, len ho necháme prekresliť
                    if hasattr(self.renderer, "render"):
                        self.renderer.render()

            return {
                "note": created_note,
                "rhythm": rhythm_info,
                "symbol": symbol,
            }

        return None
