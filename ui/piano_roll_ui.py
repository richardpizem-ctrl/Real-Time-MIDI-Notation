import pygame

class PianoRollUI:
    WHITE_KEY_WIDTH = 20
    WHITE_KEY_HEIGHT = 120
    BLACK_KEY_WIDTH = 12
    BLACK_KEY_HEIGHT = 80

    # MIDI rozsah pre 61-klávesovú Yamaha klaviatúru
    FIRST_MIDI_NOTE = 36   # C2
    LAST_MIDI_NOTE = 96    # C7

    def __init__(self, window_width=1400, window_height=200):
        pygame.init()
        self.window_width = window_width
        self.window_height = window_height

        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Piano Roll UI")

        # Stav klávesov: midi_note → farba
        self.active_keys = {}

        # Prepočítame pozície klávesov
        self.white_keys = []
        self.black_keys = []
        self._calculate_key_positions()

    # ---------------------------------------------------------
    # VÝPOČET POZÍCIÍ KLÁVES
    # ---------------------------------------------------------
    def _calculate_key_positions(self):
        white_key_order = [0, 2, 4, 5, 7, 9, 11]  # C D E F G A B
        black_key_offsets = {
            1: 0.65,  # C#
            3: 1.65,  # D#
            6: 3.65,  # F#
            8: 4.65,  # G#
            10: 5.65  # A#
        }

        white_index = 0

        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note_in_octave = midi_note % 12

            if note_in_octave in white_key_order:
                x = white_index * self.WHITE_KEY_WIDTH
                self.white_keys.append((midi_note, pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)))
                white_index += 1

        # Black keys (musíme ich umiestniť medzi biele)
        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note_in_octave = midi_note % 12
            if note_in_octave in black_key_offsets:
                octave = (midi_note - self.FIRST_MIDI_NOTE) // 12
                base_white_index = octave * 7
                x = int((base_white_index + black_key_offsets[note_in_octave]) * self.WHITE_KEY_WIDTH)
                self.black_keys.append((midi_note, pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)))

    # ---------------------------------------------------------
    # HIGHLIGHT / UNHIGHLIGHT
    # ---------------------------------------------------------
    def highlight_key(self, midi_note, color=(255, 0, 0)):
        self.active_keys[midi_note] = color

    def unhighlight_key(self, midi_note):
        if midi_note in self.active_keys:
            del self.active_keys[midi_note]

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((30, 30, 30))

        # Biele klávesy
        for midi_note, rect in self.white_keys:
            color = self.active_keys.get(midi_note, (255, 255, 255))
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

        # Čierne klávesy
        for midi_note, rect in self.black_keys:
            color = self.active_keys.get(midi_note, (0, 0, 0))
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

        pygame.display.flip()

    # ---------------------------------------------------------
    # HLAVNÁ SLUČKA (voliteľná)
    # ---------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw()
            clock.tick(60)

        pygame.quit()
