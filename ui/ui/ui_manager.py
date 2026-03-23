import pygame
from ui.piano_roll_ui import PianoRollUI

class UIManager:
    def __init__(self, width=1400, height=200):
        pygame.init()
        self.width = width
        self.height = height

        # Hlavné okno
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation - UI")

        # UI komponenty
        self.piano_roll = PianoRollUI(window_width=width, window_height=height)

        # Stav
        self.running = True
        self.clock = pygame.time.Clock()

    # ---------------------------------------------------------
    # API pre NotationProcessor
    # ---------------------------------------------------------
    def highlight_key(self, midi_note, color):
        self.piano_roll.highlight_key(midi_note, color)

    def unhighlight_key(self, midi_note):
        self.piano_roll.unhighlight_key(midi_note)

    # ---------------------------------------------------------
    # UPDATE LOOP (spustíme až na konci projektu)
    # ---------------------------------------------------------
    def update(self):
        """Volá sa v hlavnej slučke aplikácie."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

        # Kreslenie UI komponentov
        self.piano_roll.draw()

        pygame.display.flip()
        self.clock.tick(60)

    # ---------------------------------------------------------
    # Hlavná slučka (nepoužijeme hneď)
    # ---------------------------------------------------------
    def run(self):
        while self.running:
            self.update()

        pygame.quit()
