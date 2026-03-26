import pygame
import time
import math

class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Multi-note systém
        self.active_notes = []

        # Fade parametre
        self.fade_duration = 0.25
        self.fade_in_duration = 0.12

        # BPM pulz
        self.pulse_strength = 1.0

        # Trail buffer (jemné doznievanie)
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.font.init()
        self.font_size = 64
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)

    # ---------------------------------------------------------
    # BPM PULSE
    # ---------------------------------------------------------
    def update_bpm_pulse(self, bpm, timestamp):
        if bpm is None:
            self.pulse_strength = 1.0
            return

        beat_interval = 60.0 / bpm
        phase = (timestamp % beat_interval) / beat_interval
        self.pulse_strength = 1.0 + 0.15 * math.sin(phase * math.pi * 2)

    # ---------------------------------------------------------
    # NOTE ON
    # ---------------------------------------------------------
    def on_note(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))
        color = event.get("track_color", (255, 255, 255))
        velocity = event.get("velocity", 100)
        velocity_factor = min(1.0, velocity / 127)

        note_data = {
            "note": note_name,
            "color": color,

            "fade_in_start": time.time(),
            "fade_start": None,

            "bounce": 1.0 * velocity_factor,
            "glow": 1.0 * velocity_factor,

            # pre halo efekt
            "halo_strength": 1.0 * velocity_factor,
        }

        self.active_notes.append(note_data)

    # ---------------------------------------------------------
    # NOTE OFF
    # ---------------------------------------------------------
    def on_note_off(self, event):
        note_name = event.get("note_name") or str(event.get("note", "?"))

        for n in self.active_notes:
            if n["note"] == note_name and n["fade_start"] is None:
                n["fade_start"] = time.time()
                break

    # ---------------------------------------------------------
    # HALO EFEKT
    # ---------------------------------------------------------
    def draw_halo(self, surface, text_surface, rect, color, strength):
        halo_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)

        halo_color = (
            min(255, color[0]),
            min(255, color[1]),
            min(255, color[2]),
            int(80 * strength)
        )

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                halo_surface.blit(
                    text_surface,
                    (20 + dx, 20 + dy),
                    special_flags=pygame.BLEND_RGBA_ADD
                )

        halo_surface.fill(halo_color, special_flags=pygame.BLEND_RGBA_MULT)

        surface.blit(halo_surface, (rect.x - 20, rect.y - 20))

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        if not self.active_notes:
            return

        # Jemné trail doznievanie
        self.trail_surface.fill((0, 0, 0, 40), special_flags=pygame.BLEND_RGBA_SUB)
        surface.blit(self.trail_surface, (0, 0))

        y_step = self.height // (len(self.active_notes) + 1)
        y_pos = y_step

        notes_to_remove = []

        for n in self.active_notes:
            color = n["color"]

            # Fade-out
            if n["fade_start"] is not None:
                elapsed = time.time() - n["fade_start"]
                t = max(0.0, 1.0 - elapsed / self.fade_duration)

                if t <= 0:
                    notes_to_remove.append(n)
                    continue

                color = (
                    int(color[0] * t),
                    int(color[1] * t),
                    int(color[2] * t)
                )

            # Fade-in
            if n["fade_in_start"] is not None:
                t = (time.time() - n["fade_in_start"]) / self.fade_in_duration
                if t < 1.0:
                    alpha = max(0.0, min(1.0, t))
                    color = (
                        int(color[0] * alpha),
                        int(color[1] * alpha),
                        int(color[2] * alpha)
                    )
                else:
                    n["fade_in_start"] = None

            # BPM pulz
            scale = self.pulse_strength

            # Bounce
            if n["bounce"] > 0:
                scale += n["bounce"] * 0.25
                n["bounce"] *= 0.85

            # Glow
            if n["glow"] > 0:
                glow_strength = int(80 * n["glow"])
                color = (
                    min(255, color[0] + glow_strength),
                    min(255, color[1] + glow_strength),
                    min(255, color[2] + glow_strength)
                )
                n["glow"] *= 0.85

            # Render textu
            scaled_font = pygame.font.SysFont("Arial", int(self.font_size * scale), bold=True)
            text_surface = scaled_font.render(n["note"], True, color)
            text_rect = text_surface.get_rect(center=(self.width // 2, y_pos))

            # HALO
            self.draw_halo(surface, text_surface, text
