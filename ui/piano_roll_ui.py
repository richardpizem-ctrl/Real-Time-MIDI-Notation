import pygame
import time

class PianoRollUI:
    WHITE_KEY_WIDTH = 20
    WHITE_KEY_HEIGHT = 120
    BLACK_KEY_WIDTH = 12
    BLACK_KEY_HEIGHT = 80

    FIRST_MIDI_NOTE = 36   # C2
    LAST_MIDI_NOTE = 96    # C7

    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # midi_note -> (color, timestamp)
        self.active_keys = {}

        self.white_keys = []
        self.black_keys = []

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 12, bold=True)
        except Exception:
            self.font = None

        self._calculate_key_positions()

    # ---------------------------------------------------------
    # CALCULATE KEY POSITIONS
    # ---------------------------------------------------------
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
        self.white_keys.clear()
        self.black_keys.clear()

        # WHITE KEYS
        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi_note % 12
            if note in white_key_order:
                x = white_index * self.WHITE_KEY_WIDTH
                rect = pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)
                self.white_keys.append((midi_note, rect))
                white_index += 1

        # BLACK KEYS
        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi_note % 12
            if note in black_key_offsets:
                octave = (midi_note - self.FIRST_MIDI_NOTE) // 12
                base_white_index = octave * 7
                x = int((base_white_index + black_key_offsets[note]) * self.WHITE_KEY_WIDTH)
                rect = pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)
                self.black_keys.append((midi_note, rect))

    # ---------------------------------------------------------
    # KEY HIGHLIGHT
    # ---------------------------------------------------------
    def highlight_key(self, midi_note, color=(255, 80, 80)):
        """Highlight a key with fade-out animation."""
        self.active_keys[midi_note] = (color, time.time())

    def unhighlight_key(self, midi_note):
        if midi_note in self.active_keys:
            del self.active_keys[midi_note]

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        surface.fill((30, 30, 30))
        now = time.time()

        # --- WHITE KEYS ---
        for midi_note, rect in self.white_keys:
            base_color = (255, 255, 255)

            if midi_note in self.active_keys:
                color, t = self.active_keys[midi_note]
                fade = max(0.0, 1.0 - (now - t) * 1.5)
                color = (
                    int(color[0] * fade + base_color[0] * (1 - fade)),
                    int(color[1] * fade + base_color[1] * (1 - fade)),
                    int(color[2] * fade + base_color[2] * (1 - fade)),
                )
            else:
                color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        # --- BLACK KEYS ---
        for midi_note, rect in self.black_keys:
            base_color = (0, 0, 0)

            if midi_note in self.active_keys:
                color, t = self.active_keys[midi_note]
                fade = max(0.0, 1.0 - (now - t) * 1.5)
                color = (
                    int(color[0] * fade),
                    int(color[1] * fade),
                    int(color[2] * fade),
                )
            else:
                color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)

        # --- OCTAVE LABELS ---
        if self.font:
            for midi_note, rect in self.white_keys:
                if midi_note % 12 == 0:  # C note
                    octave = midi_note // 12 - 1
                    label = f"C{octave}"
                    text = self.font.render(label, True, (0, 0, 0))
                    surface.blit(text, (rect.x + 2, rect.y + self.WHITE_KEY_HEIGHT - 18))

        # --- HORIZONTAL SEPARATOR ---
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (0, self.WHITE_KEY_HEIGHT),
            (self.width, self.WHITE_KEY_HEIGHT),
            2
        )
