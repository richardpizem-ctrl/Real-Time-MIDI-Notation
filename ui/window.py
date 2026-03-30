import pygame
from ui_manager import UIManager
from real_time_processing.midi_input import MidiInput


class UIWindow:
    def __init__(self, width=1200, height=1080):
        pygame.init()
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.width = width
        self.height = height

        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.midi = MidiInput()
        self.ui = UIManager(width, height, self.midi.track_system, self.midi.notation_processor)

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.ui.handle_event(event)

            midi_events = self.midi.poll_events()
            for e in midi_events:
                if e["type"] == "note_on":
                    self.ui.on_note_on(e)
                elif e["type"] == "note_off":
                    self.ui.on_note_off(e)

            self.screen.fill((30, 30, 30))
            self.ui.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    window = UIWindow()
    window.run()
