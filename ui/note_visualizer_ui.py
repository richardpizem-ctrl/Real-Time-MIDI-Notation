import pygame
import time
import math

class NoteVisualizerUI:
    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Aktuálna nota (text + farba)
        self.current_note = None
        self.current_color = (255, 255, 255)

        # Fade-out
        self.fade_start = None
        self.fade_duration = 0.25  # sekundy

        # BPM pulz
        self.pulse_strength = 1.0

        pygame.font.init()
        self.font_size = 64
        self.font = pygame.font.SysFont("Arial", self.font_size, bold=True)

    # ---------------------------------------------------------
    # BPM PULSE (FÁZA 3 – KROK 4)
    # ---------------------------------------------------------
    def update_bpm_pulse(self, bpm, timestamp):
        if bpm is None:
            self.pulse_strength = 1.0
            return

        beat_interval = 60.0 / bpm
        phase = (timestamp % beat_interval) / beat_interval

        # jemný pulz 1.0 → 1.15
        self.pulse_strength = 1.0 + 0.15 * math.sin(phase * math.pi * 2)

    # ---------------------------------------------------------
    # API pre EventRouter / TrackSystem
    # ---------------------------------------------------------
    def on_note(self, event):
        note_name = event.get("note_name")
        if note_name is None:
            note_name = str(event.get("note", "?"))

        color = event.get("track_color", (255, 255, 255))

        self.current_note = note_name
        self.current_color = color
        self.fade_start = None  # reset fade-out

    def on_note_off(self, event):
        self.fade_start = time.time()

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self, surface):
        if not self.current_note:
            return

        color = self.current_color

        # Fade-out efekt
        if self.fade_start is not None:
            elapsed = time.time() - self.fade_start
            t = max(0.0, 1.0 - elapsed / self.fade_duration)

            if t <= 0:
                self.current_note = None
                return

            # stmavenie farby
            color = (
                int(color[0] * t),
                int(color[1] * t),
                int(color[2] * t)
            )

        # BPM pulz – zväčšenie textu
        scale = self.pulse_strength
        scaled_font = pygame.font.SysFont("Arial", int(self.font_size * scale), bold=True)

        text_surface = scaled_font.render(self.current_note, True, color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))

        surface.blit(text_surface, text_rect)
