# Note Mapper – converts MIDI note numbers to musical note names

from ..core.logger import Logger

class NoteMapper:
    NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
                  "F#", "G", "G#", "A", "A#", "B"]

    @staticmethod
    def midi_to_note(midi_number):
        """Convert MIDI note number (0–127) to note name and octave."""
        try:
            if not 0 <= midi_number <= 127:
                Logger.warning(f"Invalid MIDI note number: {midi_number}")
                return None

            note_name = NoteMapper.NOTE_NAMES[midi_number % 12]
            octave = (midi_number // 12) - 1

            return {
                "note": note_name,
                "octave": octave,
                "midi": midi_number
            }

        except Exception as e:
            Logger.error(f"NoteMapper error: {e}")
            return None

