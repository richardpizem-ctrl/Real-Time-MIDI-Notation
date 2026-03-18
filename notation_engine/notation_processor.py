from .note_mapper import NoteMapper
from .rhythm_analyzer import RhythmAnalyzer
from .symbol_manager import SymbolManager
from .notation_renderer import NotationRenderer


class NotationProcessor:
    def __init__(self):
        self.note_mapper = NoteMapper()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.symbol_manager = SymbolManager()
        self.renderer = NotationRenderer()

    def process_midi_event(self, midi_event):
        """
        Hlavná metóda, ktorá prijme MIDI udalosť a spracuje ju
        pomocou jednotlivých modulov.
        """
        midi_number = midi_event.get("note")
        velocity = midi_event.get("velocity")
        timestamp = midi_event.get("time")

        # 1. Prevod MIDI čísla na názov noty
        note_name = self.note_mapper.midi_to_note_name(midi_number)

        # 2. Analýza rytmu
        rhythm_info = self.rhythm_analyzer.analyze(timestamp)

        # 3. Výber symbolu
        symbol = self.symbol_manager.get_symbol(note_name, rhythm_info)

        # 4. Vykreslenie
        self.renderer.render(symbol)

        return {
            "note": note_name,
            "rhythm": rhythm_info,
            "symbol": symbol
        }
