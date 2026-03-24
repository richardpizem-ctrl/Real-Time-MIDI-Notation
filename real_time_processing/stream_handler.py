# real_time_processing/stream_handler.py

from notation_engine.chord_detector import detect_chord

class StreamHandler:
    def __init__(self, piano_roll_ui=None):
        """
        piano_roll_ui = inštancia PianoRollUI z ui_manager.py
        """
        self.active_notes = []
        self.piano_roll = piano_roll_ui

    def process_midi_message(self, message):
        """
        Spracuje prichádzajúcu MIDI správu.
        message.type môže byť "note_on" alebo "note_off"
        message.note je číslo MIDI noty (0–127)
        """

        # -------------------------
        # NOTE ON
        # -------------------------
        if message.type == "note_on" and message.velocity > 0:

            # pridaj do aktívnych nôt
            if message.note not in self.active_notes:
                self.active_notes.append(message.note)

            # 🔥 prepojenie na Piano Roll UI
            if self.piano_roll:
                self.piano_roll.highlight_key(
                    midi_note=message.note,
                    color=(255, 80, 80)
                )

        # -------------------------
        # NOTE OFF (alebo note_on s velocity 0)
        # -------------------------
        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):

            # odstráň z aktívnych nôt
            if message.note in self.active_notes:
                self.active_notes.remove(message.note)

            # 🔥 prepojenie na Piano Roll UI
            if self.piano_roll:
                self.piano_roll.unhighlight_key(message.note)

        # -------------------------
        # Detekcia akordu
        # -------------------------
        chord = detect_chord(self.active_notes)
        if chord:
            print(f"Detected chord: {chord.name}")
        else:
            print("No chord detected")

    # Hook pre budúce použitie
    def _on_note_created(self, note):
        pass
