import pygame
from ui_manager import UIManager
from real_time_processing.midi_input import MidiInput


class UIWindow:
    def __init__(self, width=1200, height=1080):
        pygame.init()
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.width = width
        self.height = height

        # Hlavné okno
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        # MIDI + UI
        self.midi = MidiInput()
        self.ui = UIManager(
            width,
            height,
            self.midi.track_system,
            self.midi.notation_processor
        )

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def run(self):
        running = True

        while running:
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                try:
                    self.ui.handle_event(event)
                except Exception:
                    pass

            # --- MIDI EVENTS ---
            try:
                midi_events = self.midi.poll_events()
            except Exception:
                midi_events = []

            for e in midi_events:
                etype = e.get("type")
                if etype == "note_on":
                    try:
                        self.ui.on_note_on(e)
                    except Exception:
                        pass
                elif etype == "note_off":
                    try:
                        self.ui.on_note_off(e)
                    except Exception:
                        pass

            # --- DRAW ---
            try:
                self.screen.fill((30, 30, 30))
                self.ui.draw(self.screen)
            except Exception:
                pass

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    window = UIWindow()
    window.run()
