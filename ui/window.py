# =========================================================
# UIWindow v2.0.0
# Stabilné hlavné okno pre Real-Time MIDI Notation Engine
# =========================================================

import pygame
from ui_manager import UIManager
from real_time_processing.midi_input import MidiInput


class UIWindow:
    """
    UIWindow (v2.0.0)
    -----------------
    Hlavné okno aplikácie:
        - inicializuje pygame
        - vytvára UIManager
        - spracúva MIDI eventy
        - spracúva UI eventy
        - vykresľuje UI
        - drží stabilnú hlavnú slučku (60 FPS)
    """

    def __init__(self, width: int = 1200, height: int = 1080):
        pygame.init()
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.width = int(width)
        self.height = int(height)

        # Hlavné okno
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # MIDI + UI
        self.midi = MidiInput()

        # UIManager v2.0.0
        self.ui = UIManager(
            self.width,
            self.height,
            self.midi.track_system,
            self.midi.notation_processor,
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
                except Exception as e:
                    print("[UI EVENT ERROR]", e)

            # --- MIDI EVENTS ---
            try:
                midi_events = self.midi.poll_events()
            except Exception as e:
                print("[MIDI POLL ERROR]", e)
                midi_events = []

            for e in midi_events:
                etype = e.get("type")
                if etype == "note_on":
                    try:
                        self.ui.on_note_on(e)
                    except Exception as ex:
                        print("[UI NOTE_ON ERROR]", ex)
                elif etype == "note_off":
                    try:
                        self.ui.on_note_off(e)
                    except Exception as ex:
                        print("[UI NOTE_OFF ERROR]", ex)

            # --- DRAW ---
            try:
                self.screen.fill((30, 30, 30))
                self.ui.draw(self.screen)
            except Exception as e:
                print("[UI DRAW ERROR]", e)

            pygame.display.flip()
            self.clock.tick_busy_loop(60)

        # --- CLEANUP ---
        try:
            if hasattr(self.midi, "close"):
                self.midi.close()
        except Exception as e:
            print("[MIDI CLOSE ERROR]", e)

        pygame.quit()


if __name__ == "__main__":
    window = UIWindow()
    window.run()

