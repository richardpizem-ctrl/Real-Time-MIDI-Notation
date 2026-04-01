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

        self.buttons = {
            "play": pygame.Rect(10, 10, 40, 30),
            "stop": pygame.Rect(60, 10, 40, 30),
            "loop": pygame.Rect(110, 10, 60, 30),
        }

        self.bpm = 120
        self.time_text = "00:00.0"
        self.loop_enabled = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.buttons["play"].collidepoint(pos):
                return {"action": "play"}

            if self.buttons["stop"].collidepoint(pos):
                return {"action": "stop"}

            if self.buttons["loop"].collidepoint(pos):
                self.loop_enabled = not self.loop_enabled
                return {"action": "loop", "enabled": self.loop_enabled}

        return None

    def set_bpm(self, bpm):
        self.bpm = bpm

    def set_time(self, text):
        self.time_text = text

    def draw(self, surface):
        if surface is None:
            return

        try:
            pygame.draw.rect(surface, (230, 230, 230), (0, 0, self.width, self.height))
        except Exception:
            pass

        try:
            pygame.draw.rect(surface, (0, 200, 0), self.buttons["play"])
            pygame.draw.rect(surface, (200, 0, 0), self.buttons["stop"])

            loop_color = (0, 120, 255) if self.loop_enabled else (120, 120, 120)
            pygame.draw.rect(surface, loop_color, self.buttons["loop"])
        except Exception:
            pass

        try:
            if self.font:
                play_t = self.font.render("▶", True, (0, 0, 0))
                stop_t = self.font.render("■", True, (0, 0, 0))
                loop_t = self.font.render("LOOP", True, (255, 255, 255))

                surface.blit(play_t, play_t.get_rect(center=self.buttons["play"].center))
                surface.blit(stop_t, stop_t.get_rect(center=self.buttons["stop"].center))
                surface.blit(loop_t, loop_t.get_rect(center=self.buttons["loop"].center))

                bpm_t = self.font.render(f"BPM: {self.bpm}", True, (0, 0, 0))
                time_t = self.font.render(f"TIME: {self.time_text}", True, (0, 0, 0))

                surface.blit(bpm_t, (200, 12))
                surface.blit(time_t, (350, 12))
        except Exception:
            pass
