class NoteMapper:
    NOTE_NAMES = [
        "C", "C#", "D", "D#", "E", "F",
        "F#", "G", "G#", "A", "A#", "B"
    ]

    def __init__(self):
        pass

    def midi_to_note_name(self, midi_number):
        """
        Prevod MIDI čísla (0–127) na názov noty.
        Napr. 60 -> C4, 61 -> C#4, 62 -> D4

        Stabilizované (Fáza 4):
        - ochrana pred None
        - ochrana pred nevalidnými typmi
        - ochrana pred rozsahom mimo 0–127
        - bezpečný výpočet oktávy
        - odolné voči floatom, stringom, NaN
        """

        # None → nič nevraciame
        if midi_number is None:
            return None

        # bezpečný cast
        try:
            midi_number = int(midi_number)
        except Exception:
            return None

        # rozsah MIDI
        if midi_number < 0 or midi_number > 127:
            return None

        # index v rámci oktávy
        try:
            note_index = midi_number % 12
            note_name = self.NOTE_NAMES[note_index]
        except Exception:
            return None

        # výpočet oktávy (MIDI štandard: 60 = C4)
        try:
            octave = (midi_number // 12) - 1
        except Exception:
            octave = 0

        return f"{note_name}{octave}"
