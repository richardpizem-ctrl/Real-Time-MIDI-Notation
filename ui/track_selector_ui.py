import pygame
from .track_control_manager import TrackControlManager


class TrackSelectorUI:
    def __init__(self, track_control_manager: TrackControlManager, width=1400, height=60):
        self.track_control_manager = track_control_manager
        self.width = width
        self.height = height

        self.button_width = 60
        self.button_height = 40
        self.margin = 10

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None
            self.font_small = None

        self._generate_buttons()

    # ---------------------------------------------------------
    # BUTTON GENERATION
    # ---------------------------------------------------------
    def _generate_buttons(self):
        self.track_buttons = []

        track_count = self.track_control_manager.track_count

        for i in range(track_count):
            x = self.margin + i * (self.button_width + self.margin)
            y = 10

            rect = pygame.Rect(x, y, self.button_width, self.button_height)

            self.track_buttons.append({
                "id": i,      # 0-based index
                "rect": rect
            })

    # ---------------------------------------------------------
    # CLICK HANDLING
    # ---------------------------------------------------------
    def handle_click(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return None

        for btn in self.track_buttons:
            rect = btn["rect"]
            track_id = btn["id"]

            if rect.collidepoint(pos):

                # Toggle visibility (Fáza 4)
                current = self.track_control_manager.is_visible(track_id)
                self.track_control_manager.toggle_visibility(track_id)

                # Set active track (Fáza 4)
                self.track_control_manager.select_track(track_id)

                return track_id

        return None

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None, track_activity=None):
        if surface is None:
            return

        # Fáza 4 – aktívna stopa z TrackControlManager
        system_active = self.track_control_manager.get_active_track()

        if active_track is None:
            active_track = system_active

        if track_activity is None:
            track_activity = {}

        for btn in self.track_buttons:
            track_id = btn["id"]
            rect = btn["rect"]

            # Track color (Fáza 4)
            try:
                color_hex = self.track_control_manager.get_color(track_id)
                color = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))
            except Exception:
                color = (255, 255, 255)

            # Dim if hidden
            if not self.track_control_manager.is_visible(track_id):
                color = (color[0] // 3, color[1] // 3, color[2] // 3)

            # Active track border
            is_active = (track_id == active_track)
            border_color = (0, 150, 255) if is_active else (80, 80, 80)
            border_width = 4 if is_active else 2

            # Draw button
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, border_color, rect, border_width)

            # Activity meter
            activity = track_activity.get(track_id, 0.0)
            if activity > 0:
                meter_height = int(self.button_height * activity)
                meter_rect = pygame.Rect(
                    rect.left + 3,
                    rect.bottom - meter_height - 3,
                    6,
                    meter_height
                )
                pygame.draw.rect(surface, color, meter_rect)

            # Track name
            name = f"Track {track_id + 1}"

            # Draw text
            if self.font:
                number_surface = self.font.render(str(track_id + 1), True, (0, 0, 0))
                number_rect = number_surface.get_rect(center=(rect.centerx, rect.centery - 8))
                surface.blit(number_surface, number_rect)

            if self.font_small:
                name_surface = self.font_small.render(name, True, (0, 0, 0))
                name_rect = name_surface.get_rect(center=(rect.centerx, rect.centery + 10))
                surface.blit(name_surface, name_rect)
