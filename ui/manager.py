import pygame

class TrackManagerUI:
    def __init__(self, width, height, renderer):
        self.width = width
        self.height = height
        self.renderer = renderer

        self.font = pygame.font.SysFont("Arial", 20)

        self.buttons = [
            {"track": "melody", "label": "Melody", "x": 20, "y": 10, "w": 120, "h": 40},
            {"track": "bass", "label": "Bass", "x": 160, "y": 10, "w": 120, "h": 40},
            {"track": "drums", "label": "Drums", "x": 300, "y": 10, "w": 120, "h": 40},
            {"track": "chords", "label": "Chords", "x": 440, "y": 10, "w": 120, "h": 40},
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for btn in self.buttons:
                if btn["x"] <= mx <= btn["x"] + btn["w"] and btn["y"] <= my <= btn["y"] + btn["h"]:
                    current = self.renderer.track_visible.get(btn["track"], True)
                    self.renderer.set_track_visible(btn["track"], not current)

    def draw(self, surface):
        for btn in self.buttons:
            active = self.renderer.track_visible.get(btn["track"], True)
            color = (80, 200, 120) if active else (120, 120, 120)

            pygame.draw.rect(surface, color, (btn["x"], btn["y"], btn["w"], btn["h"]), border_radius=6)

            text = self.font.render(btn["label"], True, (0, 0, 0))
            surface.blit(text, (btn["x"] + 12, btn["y"] + 8))
