# =========================================================
# TransportUI v4.3.0
# Ultra-stable transport panel for DAW (play/stop/loop/BPM/time)
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import pygame


class TransportUI:
    """
    TransportUI (v4.3.0)
    --------------------
    Minimal, ultra-stable transport panel for DAW-style applications.

    Features:
        - play / stop / rewind
        - loop toggle
        - BPM +/- controls
        - time display
        - real-time safe
        - no exceptions
        - clean English API
        - UIManager-compatible
        - ready for v5 (skins, animations, AI assist)
    """

    __slots__ = (
        "width",
        "height",
        "font",
        "buttons",
        "bpm",
        "time_text",
        "loop_enabled",
        "is_playing",
    )

    def __init__(self, width: int = 1400, height: int = 50):
        self.width = int(width)
        self.height = int(height)

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 20, bold=True)
        except Exception:
            self.font = None

        # -----------------------------------------------------
        # BUTTONS
        # -----------------------------------------------------
        self.buttons = {
            "rewind": pygame.Rect(10, 10, 40, 30),
            "play": pygame.Rect(60, 10, 40, 30),
            "stop": pygame.Rect(110, 10, 40, 30),
            "loop": pygame.Rect(160, 10, 60, 30),
            "bpm_minus": pygame.Rect(240, 10, 30, 30),
            "bpm_plus": pygame.Rect(310, 10, 30, 30),
        }

        # -----------------------------------------------------
        # STATE
        # -----------------------------------------------------
        self.bpm = 120
        self.time_text = "00:00.0"
        self.loop_enabled = False
        self.is_playing = False

    # ---------------------------------------------------------
    # NO-OP API (UIManager compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event):
        """Handle mouse clicks and return action dict or None."""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        pos = event.pos
        buttons = self.buttons

        if buttons["rewind"].collidepoint(pos):
            self.is_playing = False
            return {"action": "rewind"}

        if buttons["play"].collidepoint(pos):
            self.is_playing = True
            return {"action": "play"}

        if buttons["stop"].collidepoint(pos):
            self.is_playing = False
            return {"action": "stop"}

        if buttons["loop"].collidepoint(pos):
            self.loop_enabled = not self.loop_enabled
            return {"action": "loop", "enabled": self.loop_enabled}

        if buttons["bpm_minus"].collidepoint(pos):
            self.bpm = max(20, self.bpm - 1)
            return {"action": "bpm", "value": self.bpm}

        if buttons["bpm_plus"].collidepoint(pos):
            self.bpm = min(300, self.bpm + 1)
            return {"action": "bpm", "value": self.bpm}

        return None

    # ---------------------------------------------------------
    # SETTERS
    # ---------------------------------------------------------
    def set_bpm(self, bpm):
        """Safely set BPM (20–300)."""
        try:
            bpm = int(bpm)
        except Exception:
            return
        self.bpm = max(20, min(300, bpm))

    def set_time(self, text):
        """Set time display text."""
        if isinstance(text, str):
            self.time_text = text

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        """Draw the transport panel."""
        if surface is None:
            return

        # Background
        pygame.draw.rect(surface, (230, 230, 230), (0, 0, self.width, self.height))

        buttons = self.buttons

        # Button colors
        pygame.draw.rect(surface, (80, 80, 80), buttons["rewind"])
        pygame.draw.rect(
            surface,
            (0, 200, 0) if not self.is_playing else (0, 150, 0),
            buttons["play"],
        )
        pygame.draw.rect(surface, (200, 0, 0), buttons["stop"])

        loop_color = (0, 120, 255) if self.loop_enabled else (120, 120, 120)
        pygame.draw.rect(surface, loop_color, buttons["loop"])

        pygame.draw.rect(surface, (180, 180, 180), buttons["bpm_minus"])
        pygame.draw.rect(surface, (180, 180, 180), buttons["bpm_plus"])

        # Text rendering
        if self.font:
            font = self.font

            # Icons
            rewind_t = font.render("⏪", True, (255, 255, 255))
            play_t = font.render("▶", True, (0, 0, 0))
            stop_t = font.render("■", True, (0, 0, 0))
            loop_t = font.render("LOOP", True, (255, 255, 255))

            minus_t = font.render("-", True, (0, 0, 0))
            plus_t = font.render("+", True, (0, 0, 0))

            # Draw icons
            surface.blit(rewind_t, rewind_t.get_rect(center=buttons["rewind"].center))
            surface.blit(play_t, play_t.get_rect(center=buttons["play"].center))
            surface.blit(stop_t, stop_t.get_rect(center=buttons["stop"].center))
            surface.blit(loop_t, loop_t.get_rect(center=buttons["loop"].center))

            surface.blit(minus_t, minus_t.get_rect(center=buttons["bpm_minus"].center))
            surface.blit(plus_t, plus_t.get_rect(center=buttons["bpm_plus"].center))

            # BPM text
            bpm_t = font.render(f"BPM: {self.bpm}", True, (0, 0, 0))
            surface.blit(bpm_t, (360, 12))

            # Time display box
            pygame.draw.rect(surface, (255, 255, 255), (500, 10, 150, 30))
            pygame.draw.rect(surface, (0, 0, 0), (500, 10, 150, 30), 2)

            time_t = font.render(self.time_text, True, (0, 0, 0))
            surface.blit(time_t, (510, 12))
