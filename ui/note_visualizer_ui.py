import pygame
import time

class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Aktuálna nota (text + farba)
        self.current_note = None
        self.current_color = (255, 255, 255)

        # Fade-out
        self.fade_start = None
        self.fade_duration = 0.25  # sekundy

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 64, bold=True)

    # ---------------------------------------------------------
    # API pre EventRouter / TrackSystem
    # ---------------------------------------------------------
    def on_note(self, event):
        """
        event = {
            "note": int,
            "note_name": str,
            "track_color": (r,g,b),
            ...
        }
        """
        note_name = event.get("note_name")
        if note_name is None:
            note_name = str(event.get("note", "?"))

        color = event.get("track_color", (255, 255, 255))

        self.current_note = note_name
        self.current_color = color
        self.fade_start = None  # reset fade-out

    def on_note_off(self, event):
        """Spustí fade-out pri note_off."""
        self.fade_start = time.time()

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        if not self.current_note:
            return

        color = self.current_color

        # Fade-out efekt
        if self.fade_start is not None:
            elapsed = time.time() - self.fade_start
            t = max(0.0, 1.0 - elapsed / self.fade_duration)

            if t <= 0:
                self.current_note = None
                return

            # stmavenie farby
            color = (
                int(color[0] * t),
                int(color[1] * t),
                int(color[2] * t)
            )

        text_surface = self.font.render(self.current_note, True, color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

        surface.blit(text_surface, text_rect)
