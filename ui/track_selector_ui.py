import pygame

class TrackSelectorUI:
    def __init__(self, track_system, width=1400, height=60):
        self.track_system = track_system
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

    def _generate_buttons(self):
        self.track_buttons = []

        try:
            track_count = len(getattr(self.track_system, "tracks", {}))
        except Exception:
            track_count = 0

        for i in range(track_count):
            track_id = i
            x = self.margin + i * (self.button_width + self.margin)
            y = 10

            try:
                rect = pygame.Rect(x, y, self.button_width, self.button_height)
            except Exception:
                continue

            self.track_buttons.append({
                "id": track_id,
                "rect": rect
            })

    def handle_click(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return None

        for btn in self.track_buttons:
            rect = btn.get("rect")
            track_id = btn.get("id")

            if rect is None or track_id is None:
                continue

            try:
                if rect.collidepoint(pos):
                    try:
                        current = self.track_system.is_visible(track_id)
                        self.track_system.set_visible(track_id, not current)
                    except Exception:
                        pass

                    try:
                        self.track_system.set_active_track(track_id)
                    except Exception:
                        pass

                    return track_id
            except Exception:
                continue

        return None

    def draw(self, surface, active_track=None, track_activity=None):
        if surface is None:
            return

        try:
            system_active = self.track_system.get_active_track()
        except Exception:
            system_active = None

        if active_track is None:
            active_track = system_active

        if track_activity is None:
            track_activity = {}

        for btn in self.track_buttons:
            track_id = btn.get("id")
            rect = btn.get("rect")

            if rect is None or track_id is None:
                continue

            try:
                color = self.track_system.get_color(track_id)
                if not (
                    isinstance(color, (tuple, list)) and
                    len(color) == 3 and
                    all(isinstance(c, int) for c in color)
                ):
                    color = (255, 255, 255)
            except Exception:
                color = (255, 255, 255)

            try:
                if not self.track_system.is_visible(track_id):
                    color = (color[0] // 3, color[1] // 3, color[2] // 3)
            except Exception:
                pass

            is_active = (track_id == active_track)

            border_color = (0, 150, 255) if is_active else (80, 80, 80)
            border_width = 4 if is_active else 2

            try:
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, border_color, rect, border_width)
            except Exception:
                continue

            try:
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
            except Exception:
                pass

            try:
                if hasattr(self.track_system, "get_name"):
                    name = self.track_system.get_name(track_id)
                else:
                    name = None
            except Exception:
                name = None

            if not name:
                name = f"Track {track_id + 1}"

            try:
                if self.font:
                    number_surface = self.font.render(str(track_id + 1), True, (0, 0, 0))
                    number_rect = number_surface.get_rect(center=(rect.centerx, rect.centery - 8))
                    surface.blit(number_surface, number_rect)

                if self.font_small:
                    name_surface = self.font_small.render(name, True, (0, 0, 0))
                    name_rect = name_surface.get_rect(center=(rect.centerx, rect.centery + 10))
                    surface.blit(name_surface, name_rect)
            except Exception:
                pass
