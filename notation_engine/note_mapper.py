class NoteMapper:
    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
                  "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self):
        pass

    def midi_to_note_name(self, midi_number):
        """
        Prevod MIDI čísla (0–127) na názov noty.
        Napr. 60 -> C4, 61 -> C#4, 62 -> D4
        Stabilizované:
        - ochrana pred None
        - ochrana pred nevalidnými typmi
        - ochrana pred rozsahom mimo 0–127
        """
        if midi_number is None:
            return None

        try:
            midi_number = int(midi_number)
        except Exception:
            return None

        if midi_number < 0 or midi_number > 127:
            return None

        note_index = midi_number % 12
        octave = (midi_number // 12) - 1

        try:
            note_name = self.NOTE_NAMES[note_index]
        except Exception:
            return None

        return f"{note_name}{octave}"
