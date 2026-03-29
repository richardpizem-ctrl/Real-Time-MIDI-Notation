import pygame

class PianoRollUI:
    WHITE_KEY_WIDTH = 20
    WHITE_KEY_HEIGHT = 120
    BLACK_KEY_WIDTH = 12
    BLACK_KEY_HEIGHT = 80

    FIRST_MIDI_NOTE = 36
    LAST_MIDI_NOTE = 96

    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height
        self.active_keys = {}
        self.white_keys = []
        self.black_keys = []
        self._calculate_key_positions()

    def _calculate_key_positions(self):
        white_key_order = [0, 2, 4, 5, 7, 9, 11]
        black_key_offsets = {
            1: 0.65,
            3: 1.65,
            6: 3.65,
            8: 4.65,
            10: 5.65
        }

        white_index = 0

        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note_in_octave = midi_note % 12
            if note_in_octave in white_key_order:
                x = white_index * self.WHITE_KEY_WIDTH
                rect = pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)
                self.white_keys.append((midi_note, rect))
                white_index += 1

        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note_in_octave = midi_note % 12
            if note_in_octave in black_key_offsets:
                octave = (midi_note - self.FIRST_MIDI_NOTE) // 12
                base_white_index = octave * 7
                x = int((base_white_index + black_key_offsets[note_in_octave]) * self.WHITE_KEY_WIDTH)
                rect = pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)
                self.black_keys.append((midi_note, rect))

    def highlight_key(self, midi_note, color=(255, 0, 0)):
        self.active_keys[midi_note] = color

    def unhighlight_key(self, midi_note):
        if midi_note in self.active_keys:
            del self.active_keys[midi_note]

    def draw(self, surface):
        surface.fill((30, 30, 30))

        for midi_note, rect in self.white_keys:
            color = self.active_keys.get(midi_note, (255, 255, 255))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        for midi_note, rect in self.black_keys:
            color = self.active_keys.get(midi_note, (0, 0, 0))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)
