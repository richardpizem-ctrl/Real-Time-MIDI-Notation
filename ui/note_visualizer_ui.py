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
    # API pre NotationProcessor / UIManager
    # ---------------------------------------------------------
    def set_note(self, note_name, color=None):
        """Nastaví aktuálnu notu na zobrazenie."""
        self.current_note = note_name
        if color:
            self.current_color = color

    def clear_note(self):
        """Vymaže aktuálnu notu."""
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
