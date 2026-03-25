import pygame

class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Aktuálna nota (text + farba)
        self.current_note = None
        self.current_color = (255, 255, 255)

        # Font pre veľký text
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 64, bold=True)

    # ---------------------------------------------------------
    # API pre EventRouter / TrackSystem
    # ---------------------------------------------------------
    def on_note(self, event):
        """
        event = dict:
        {
            "note": int,
            "note_name": str,
            "track_color": (r,g,b),
            ...
        }
        """
        note_name = event.get("note_name", None)
        color = event.get("track_color", (255, 255, 255))

        self.current_note = note_name
        self.current_color = color

    def on_note_off(self, event):
        """Vymaže aktuálnu notu pri note_off."""
        self.current_note = None

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        if not self.current_note:
            return

        text_surface = self.font.render(self.current_note, True, self.current_color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

        surface.blit(text_surface, text_rect)
