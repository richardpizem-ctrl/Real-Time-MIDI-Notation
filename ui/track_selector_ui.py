import pygame

class TrackSelectorUI:
    def __init__(self, track_manager, width=1400, height=60):
        """
        track_manager = inštancia TrackManagera
        """
        self.track_manager = track_manager
        self.width = width
        self.height = height

        self.button_width = 60
        self.button_height = 40
        self.margin = 10

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)

        self._generate_buttons()

    # ---------------------------------------------------------
    # VYTVORENIE 16 TLAČIDIEL PRE TRACKY (Yamaha štandard)
    # ---------------------------------------------------------
    def _generate_buttons(self):
        self.track_buttons = []

        for track_id in range(1, 17):  # 1–16
            x = self.margin + (track_id - 1) * (self.button_width + self.margin)
            y = 10

            rect = pygame.Rect(x, y, self.button_width, self.button_height)

            self.track_buttons.append({
                "id": track_id,
                "rect": rect
            })

    # ---------------------------------------------------------
    # KLIKANIE MYŠOU – toggle visibility
    # ---------------------------------------------------------
    def handle_click(self, pos):
        """Spracuje kliknutie na track button."""
        for btn in self.track_buttons:
            if btn["rect"].collidepoint(pos):
                track_id = btn["id"]

                # Toggle visibility
                current = self.track_manager.is_visible(track_id)
                self.track_manager.set_visible(track_id, not current)

                # Nastavenie aktívnej stopy
                self.track_manager.track_system.set_active_track(track_id)

                return track_id
        return None

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        active_id = self.track_manager.get_active_track()

        for btn in self.track_buttons:
            track_id = btn["id"]
            rect = btn["rect"]

            # Farba tracku z TrackManagera
            color = self.track_manager.get_color(track_id)

            # Viditeľnosť – ak je vypnutá, stmavíme farbu
            if not self.track_manager.is_visible(track_id):
                color = (color[0] // 3, color[1] // 3, color[2] // 3)

            # Aktívny track má hrubý rámik
            border_color = (255, 255, 255) if track_id == active_id else (80, 80, 80)
            border_width = 4 if track_id == active_id else 2

            # Telo tlačidla
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, border_color, rect, border_width)

            # Text (číslo tracku)
            text_surface = self.font.render(str(track_id), True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)
