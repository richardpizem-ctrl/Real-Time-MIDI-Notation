import pygame

class TransportUI:
    def __init__(self, width=1400, height=50):
        self.width = width
        self.height = height

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 20, bold=True)
        except Exception:
            self.font = None

        # --- BUTTONS ---
        self.buttons = {
            "rewind": pygame.Rect(10, 10, 40, 30),
            "play": pygame.Rect(60, 10, 40, 30),
            "stop": pygame.Rect(110, 10, 40, 30),
            "loop": pygame.Rect(160, 10, 60, 30),
            "bpm_minus": pygame.Rect(240, 10, 30, 30),
            "bpm_plus": pygame.Rect(310, 10, 30, 30),
        }

        # --- STATE ---
        self.bpm = 120
        self.time_text = "00:00.0"
        self.loop_enabled = False
        self.is_playing = False

    # ---------------------------------------------------------
    # EVENT HANDLING
    # ---------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.buttons["rewind"].collidepoint(pos):
                self.is_playing = False
                return {"action": "rewind"}

            if self.buttons["play"].collidepoint(pos):
                self.is_playing = True
                return {"action": "play"}

            if self.buttons["stop"].collidepoint(pos):
                self.is_playing = False
                return {"action": "stop"}

            if self.buttons["loop"].collidepoint(pos):
                self.loop_enabled = not self.loop_enabled
                return {"action": "loop", "enabled": self.loop_enabled}

            if self.buttons["bpm_minus"].collidepoint(pos):
                self.bpm = max(20, self.bpm - 1)
                return {"action": "bpm", "value": self.bpm}

            if self.buttons["bpm_plus"].collidepoint(pos):
                self.bpm = min(300, self.bpm + 1)
                return {"action": "bpm", "value": self.bpm}

        return None

    # ---------------------------------------------------------
    # SETTERS
    # ---------------------------------------------------------
    def set_bpm(self, bpm):
        self.bpm = max(20, min(300, bpm))

    def set_time(self, text):
        self.time_text = text

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        if surface is None:
            return

        # Background
        pygame.draw.rect(surface, (230, 230, 230), (0, 0, self.width, self.height))

        # --- BUTTON COLORS ---
        pygame.draw.rect(surface, (80, 80, 80), self.buttons["rewind"])
        pygame.draw.rect(surface, (0, 200, 0) if not self.is_playing else (0, 150, 0), self.buttons["play"])
        pygame.draw.rect(surface, (200, 0, 0), self.buttons["stop"])

        loop_color = (0, 120, 255) if self.loop_enabled else (120, 120, 120)
        pygame.draw.rect(surface, loop_color, self.buttons["loop"])

        pygame.draw.rect(surface, (180, 180, 180), self.buttons["bpm_minus"])
        pygame.draw.rect(surface, (180, 180, 180), self.buttons["bpm_plus"])

        # --- TEXT ---
        if self.font:
            # Icons
            rewind_t = self.font.render("⏪", True, (255, 255, 255))
            play_t = self.font.render("▶", True, (0, 0, 0))
            stop_t = self.font.render("■", True, (0, 0, 0))
            loop_t = self.font.render("LOOP", True, (255, 255, 255))

            minus_t = self.font.render("-", True, (0, 0, 0))
            plus_t = self.font.render("+", True, (0, 0, 0))

            # Draw icons
            surface.blit(rewind_t, rewind_t.get_rect(center=self.buttons["rewind"].center))
            surface.blit(play_t, play_t.get_rect(center=self.buttons["play"].center))
            surface.blit(stop_t, stop_t.get_rect(center=self.buttons["stop"].center))
            surface.blit(loop_t, loop_t.get_rect(center=self.buttons["loop"].center))

            surface.blit(minus_t, minus_t.get_rect(center=self.buttons["bpm_minus"].center))
            surface.blit(plus_t, plus_t.get_rect(center=self.buttons["bpm_plus"].center))

            # BPM text
            bpm_t = self.font.render(f"BPM: {self.bpm}", True, (0, 0, 0))
            surface.blit(bpm_t, (360, 12))

            # TIME DISPLAY
            pygame.draw.rect(surface, (255, 255, 255), (500, 10, 150, 30))
            pygame.draw.rect(surface, (0, 0, 0), (500, 10, 150, 30), 2)

            time_t = self.font.render(self.time_text, True, (0, 0, 0))
            surface.blit(time_t, (510, 12))
