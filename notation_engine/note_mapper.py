class NoteMapper:
    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self):
        pass

    def midi_to_note_name(self, midi_number):
        """
        Prevod MIDI čísla (0–127) na názov noty.
        Napr. 60 -> C4, 61 -> C#4, 62 -> D4
        """
        if midi_number is None:
            return None

        note_index = midi_number % 12
        octave = (midi_number // 12) - 1
        note_name = self.NOTE_NAMES[note_index]

        return f"{note_name}{octave}"

