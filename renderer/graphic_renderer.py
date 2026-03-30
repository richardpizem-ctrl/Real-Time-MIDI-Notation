import pygame
import math
from typing import List, Dict, Any, Tuple, Optional


class GraphicNotationRenderer:
    def __init__(self, width, height, track_manager):
        self.width = width
        self.height = height
        self.track_manager = track_manager

        try:
            self.surface = pygame.Surface((width, height))
        except Exception:
            self.surface = None

        try:
            self.font = pygame.font.SysFont("Arial", 18)
        except Exception:
            self.font = None

        self.staff_cache = None
        self.staff_cache_width = width
        self.staff_cache_height = 140

        self.margin_left = 40
        self.margin_top = 20
        self.note_spacing = 28
        self.staff_line_spacing = 12

        self.scroll_x = 0.0
        self.scroll_speed = 2.2

    # ---------------------------------------------------------
    # STAFF LINES (CACHED)
    # ---------------------------------------------------------
    def _render_staff_lines(self):
        if self.staff_cache is not None:
            return self.staff_cache

        try:
            surf = pygame.Surface(
                (self.staff_cache_width, self.staff_cache_height),
                pygame.SRCALPHA
            )
            surf.fill((0, 0, 0, 0))

            y_start = self.margin_top
            for i in range(5):
                y = y_start + i * self.staff_line_spacing
                pygame.draw.line(
                    surf,
                    (200, 200, 200),
                    (self.margin_left, y),
                    (self.width - 20, y),
                    2
                )

            self.staff_cache = surf
            return surf

        except Exception:
            return pygame.Surface((self.width, 1))

    # ---------------------------------------------------------
    # NOTE POSITIONING
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi: int) -> float:
        try:
            return self.margin_top + (60 - midi) * 1.1
        except Exception:
            return float(self.margin_top)

    def _time_to_x(self, timestamp: float) -> float:
        try:
            return self.margin_left + timestamp * self.note_spacing - self.scroll_x
        except Exception:
            return float(self.margin_left)

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _get_track_color(self, track_id: int, active_track_id: Optional[int]) -> Tuple[int, int, int]:
        try:
            base_color = self.track_manager.get_color(track_id)
        except Exception:
            base_color = (255, 255, 255)

        if active_track_id is None or track_id != active_track_id:
            return base_color

        # Jemné zvýraznenie aktívneho tracku
        r, g, b = base_color
        r = min(255, int(r * 1.2) + 10)
        g = min(255, int(g * 1.2) + 10)
        b = min(255, int(b * 1.2) + 10)
        return (r, g, b)

    # ---------------------------------------------------------
    # DRAW NOTE HEAD
    # ---------------------------------------------------------
    def _draw_note(self, surface, x: float, y: float, color: Tuple[int, int, int]):
        try:
            rect = pygame.Rect(int(x), int(y), 16, 12)
            pygame.draw.ellipse(surface, color, rect)
            pygame.draw.ellipse(surface, (0, 0, 0), rect, 2)
        except Exception:
            pass

    # ---------------------------------------------------------
    # GROUP NOTES INTO CHORDS
    # ---------------------------------------------------------
    def _group_notes(self, notes: List[Dict[str, Any]]) -> Dict[Tuple[float, int], List[Dict[str, Any]]]:
        groups: Dict[Tuple[float, int], List[Dict[str, Any]]] = {}
        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch") or note.get("note")
            track_id = note.get("track_id")
            timestamp = note.get("timestamp", 0.0)

            if midi is None or track_id is None:
                continue

            key = (float(timestamp), int(track_id))
            if key not in groups:
                groups[key] = []
            groups[key].append(note)

        return groups

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, notes):
        if self.surface is None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                return None

        try:
            self.surface.fill((25, 25, 25))
        except Exception:
            pass

        try:
            staff = self._render_staff_lines()
            self.surface.blit(staff, (0, 0))
        except Exception:
            pass

        if not isinstance(notes, (list, tuple)):
            return self.surface

        # Auto-scroll
        self.scroll_x += self.scroll_speed

        # Aktívny track
        try:
            active_track_id = self.track_manager.get_active_track()
        except Exception:
            active_track_id = None

        # Zoskupenie nôt do akordov podľa (timestamp, track_id)
        grouped = self._group_notes(list(notes))

        # Kreslenie akordov
        for (timestamp, track_id), chord_notes in grouped.items():
            # Viditeľnosť tracku
            try:
                if not self.track_manager.is_visible(track_id):
                    continue
            except Exception:
                pass

            base_x = self._time_to_x(timestamp)
            color = self._get_track_color(track_id, active_track_id)

            # Akord – mierne horizontálne posuny, aby sa noty neprekrývali
            for idx, note in enumerate(chord_notes):
                midi = note.get("pitch") or note.get("note")
                if midi is None:
                    continue

                y = self._pitch_to_y(int(midi))
                x = base_x + idx * 6  # jemné rozostupy v akorde
                self._draw_note(self.surface, x, y, color)

        return self.surface
