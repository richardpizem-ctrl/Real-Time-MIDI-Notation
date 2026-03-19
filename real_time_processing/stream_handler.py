# real_time_processing/stream_handler.py

from notation_engine.chord_detector import detect_chord


class StreamHandler:
    def __init__(self):
        # Zoznam aktuálne stlačených MIDI nôt
        self.active_notes = []

    def process_midi_message(self, message):
        """
        Spracuje prichádzajúcu MIDI správu.
        message.type môže byť "note_on" alebo "note_off"
        message.note je číslo MIDI noty (0–127)
        """

        # NOTE ON
        if message.type == "note_on":
            if message.note not in self.active_notes:
                self.active_notes.append(message.note)

        # NOTE OFF
        elif message.type == "note_off":
            if message.note in self.active_notes:
                self.active_notes.remove(message.note)

        # --- Detekcia akordu po každej zmene ---
        chord = detect_chord(self.active_notes)
        if chord:
            print(f"Detected chord: {chord.name}")
        else:
            print("No chord detected")

    def _on_note_created(self, note):
        """
        Toto je hook, ktorý môžeš neskôr použiť na:
        - vykreslenie noty
        - farbenie podľa akordu
        - posielanie do UI
        """
        pass

              


