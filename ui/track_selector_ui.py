import pygame

class TrackSelectorUI:
    def __init__(self, track_system, width=1400, height=60):
        """
        track_system = inštancia TrackSystemu
        """
        self.track_system = track_system
        self.width = width
        self.height = height

        self.button_width = 60
        self.button_height = 40
        self.margin = 10

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)

        self._generate_buttons()

    # ---------------------------------------------------------
    # VYTVORENIE TLAČIDIEL PRE TRACKY
    # ---------------------------------------------------------
    def _generate_buttons(self):
        self.track_buttons = []

        track_count = len(self.track_system.tracks)

        for i in range(track_count):
            track_id = i  # TrackSystem používa indexy 0–15

            x = self.margin + i * (self.button_width + self.margin)
            y = 10

            rect = pygame.Rect(x, y, self.button_width, self.button_height)

            self.track_buttons.append({
                "id": track_id,
                "rect": rect
            })

    # ---------------------------------------------------------
    # KLIKANIE MYŠOU
    # ---------------------------------------------------------
    def handle_click(self, pos):
        """Spracuje kliknutie na track button."""
        for btn in self.track_buttons:
            if btn["rect"].collidepoint(pos):
                self.track_system.set_active_track(btn["id"])
                return btn["id"]
        return None

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        active_id = self.track_system.active_track_id

        for btn in self.track_buttons:
            track_id = btn["id"]
            rect = btn["rect"]

            # Farba tracku (vždy aktuálna)
            color = self.track_system.get_track_color(track_id)

            # Aktívny track má hrubý rámik
            border_color = (255, 255, 255) if track_id == active_id else (80, 80, 80)
            border_width = 4 if track_id == active_id else 2

            # Telo tlačidla
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, border_color, rect, border_width)

            # Text (číslo tracku)
            text_surface = self.font.render(str(track_id + 1), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
