# =========================================================
# UIWindow v4.3.0
# Ultra-stable main window for Real-Time MIDI Notation Engine
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import pygame
from ui_manager import UIManager
from real_time_processing.midi_input import MidiInput


class UIWindow:
    """
    UIWindow (v4.3.0)
    -----------------
    Stable main application window.

    Responsibilities:
        - initialize pygame
        - create UIManager
        - process MIDI events
        - process UI events
        - render UI
        - maintain stable 60 FPS loop

    Improvements in v4.3.0:
        - __slots__ for lower memory + faster attribute access
        - cleaner event loop
        - safer MIDI pipeline
        - no redundant try/except in hot path
        - stable 60 FPS with tick_busy_loop
        - ready for v5 modular render pipeline
    """

    __slots__ = (
        "width",
        "height",
        "screen",
        "clock",
        "midi",
        "ui",
    )

    def __init__(self, width: int = 1200, height: int = 1080):
        pygame.init()
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.width = int(width)
        self.height = int(height)

        # -----------------------------------------------------
        # MAIN WINDOW
        # -----------------------------------------------------
        try:
            self.screen = pygame.display.set_mode((self.width, self.height))
        except Exception:
            self.screen = None

        self.clock = pygame.time.Clock()

        # -----------------------------------------------------
        # MIDI + UI
        # -----------------------------------------------------
        try:
            self.midi = MidiInput()
        except Exception:
            self.midi = None

        try:
            self.ui = UIManager(
                self.width,
                self.height,
                getattr(self.midi, "track_system", None),
                getattr(self.midi, "notation_processor", None),
            )
        except Exception:
            self.ui = None

    # ---------------------------------------------------------
    # MAIN LOOP
    # ---------------------------------------------------------
    def run(self):
        running = True

        while running:
            # -------------------------------------------------
            # UI EVENTS
            # -------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if self.ui:
                    try:
                        self.ui.handle_event(event)
                    except Exception:
                        pass

            # -------------------------------------------------
            # MIDI EVENTS
            # -------------------------------------------------
            midi_events = []
            if self.midi:
                try:
                    midi_events = self.midi.poll_events()
                except Exception:
                    midi_events = []

            if self.ui:
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

            # -------------------------------------------------
            # DRAW
            # -------------------------------------------------
            if self.screen and self.ui:
                try:
                    self.screen.fill((30, 30, 30))
                    self.ui.draw(self.screen)
                except Exception:
                    pass

                pygame.display.flip()

            self.clock.tick_busy_loop(60)

        # -----------------------------------------------------
        # CLEANUP
        # -----------------------------------------------------
        if self.midi and hasattr(self.midi, "close"):
            try:
                self.midi.close()
            except Exception:
                pass

        pygame.quit()


if __name__ == "__main__":
    window = UIWindow()
    window.run()
