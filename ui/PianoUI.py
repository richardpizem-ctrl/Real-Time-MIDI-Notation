import pygame

class PianoUI:
    WHITE_KEY_WIDTH = 22
    WHITE_KEY_HEIGHT = 140
    BLACK_KEY_WIDTH = 14
    BLACK_KEY_HEIGHT = 90

    FIRST_MIDI_NOTE = 36
    LAST_MIDI_NOTE = 96

    def __init__(self, width=1500, height=180):
        self.width = width
        self.height = height
        self.active_keys = {}
        self.white_keys = []
        self.black_keys = []
        self._calculate_positions()

    def _calculate_positions(self):
        white_order = [0, 2, 4, 5, 7, 9, 11]
        black_offsets = {
            1: 0.65,
            3: 1.65,
            6: 3.65,
            8: 4.65,
            10: 5.65
        }

        white_index = 0

        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi % 12
            if note in white_order:
                x = white_index * self.WHITE_KEY_WIDTH
                rect = pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)
                self.white_keys.append((midi, rect))
                white_index += 1

        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi % 12
            if note in black_offsets:
                octave = (midi - self.FIRST_MIDI_NOTE) // 12
                base = octave * 7
                x = int((base + black_offsets[note]) * self.WHITE_KEY_WIDTH)
                rect = pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)
                self.black_keys.append((midi, rect))

    def highlight(self, midi_note, color=(255, 80, 80)):
        self.active_keys[midi_note] = color

    def unhighlight(self, midi_note):
        if midi_note in self.active_keys:
            del self.active_keys[midi_note]

    def draw(self, surface):
        surface.fill((25, 25, 25))

        for midi, rect in self.white_keys:
            color = self.active_keys.get(midi, (255, 255, 255))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        for midi, rect in self.black_keys:
            color = self.active_keys.get(midi, (0, 0, 0))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)
