import pygame
import math
import time

from ui.staff_ui import StaffUI
from ui.piano_roll_ui import PianoRollUI
from ui.note_visualizer_ui import NoteVisualizerUI

# MIDI routing
from real_time_processing.stream_handler import StreamHandler
from midi_input.event_router import EventRouter


class UIManager:
    def __init__(self, width=1400, height=600):
        pygame.init()
        self.width = width
        self.height = height

        # Hlavné okno
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation")

        # UI komponenty
        self.staff_ui = StaffUI(width, 200)
        self.piano_ui = PianoRollUI(width, 200)
        self.note_visualizer = NoteVisualizerUI(width, 200)

        # EventRouter (prepája MIDI → EventBus → UI)
        self.event_router = EventRouter(event_bus=None, piano_roll_ui=self.piano_ui)

        # StreamHandler (prepája MIDI → UI)
        self.stream_handler = StreamHandler(piano_roll_ui=self.piano_ui)
        self.stream_handler.event_router = self.event_router

        # ---------------------------------------------------------
        # BPM LABEL + BPM VIZUALIZÁCIA
        # ---------------------------------------------------------
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.current_bpm_text = "BPM: —"

        self.bpm_value = None
        self.last_bpm = None
        self.beat_interval = 1.0
        self.last_beat_time = time.time()
        self.stability = 1.0

        # Dýchanie kruhu
        self.breath_phase = 0.0

        # História BPM
        self.bpm_history = []
        self.max_history = 60

        # Metronóm klik
        self.metronome_flash = 0.0

    # ---------------------------------------------------------
    # BPM UPDATE – text, interval, stabilita, história
    # ---------------------------------------------------------
    def update_bpm(self, bpm):
        if bpm is None:
            self.current_bpm_text = "BPM: —"
            self.bpm_value = None
            return

        self.current_bpm_text = f"BPM: {bpm:.1f}"
        self.bpm_value = bpm
        self.beat_interval = 60.0 / bpm

        # Stabilita
        if self.last_bpm is not None:
            diff = abs(self.last_bpm - bpm)
            self.stability = max(0.0, min(1.0, 1.0 - diff / 10.0))
        self.last_bpm = bpm

        # História BPM
        self.bpm_history.append(bpm)
        if len(self.bpm_history) > self.max_history:
            self.bpm_history.pop(0)

    # ---------------------------------------------------------
    # BPM VIZUALIZÁCIA
    # ---------------------------------------------------------
    def draw_bpm_visual(self):
        x, y = 120, 30

        # Farebný gradient podľa tempa (60–180 BPM)
        if self.bpm_value is not None:
            tempo_norm = (self.bpm_value - 60.0) / 120.0
            tempo_norm = max(0.0, min(1.0, tempo_norm))
        else:
            tempo_norm = 0.0

        base_color = (
            int(tempo_norm * 255),          # červená rastie s tempom
            int((1.0 - tempo_norm) * 255),  # zelená klesá s tempom
            100
        )

        # Čas od posledného beatu
        now = time.time()
        beat_progress = (now - self.last_beat_time) / self.beat_interval

        # Nový beat → metronómový klik
        if beat_progress >= 1.0:
            self.last_beat_time = now
            beat_progress = 0.0
            self.metronome_flash = 1.0

        # Pulzujúci hlavný kruh
        base_radius = 20 + 10 * (1 - beat_progress)

        # Jemné dýchanie
        self.breath_phase += 0.05
        breathing = 3 * math.sin(self.breath_phase)

        radius = int(base_radius + breathing)

        # Metronóm klik – malý blikajúci štvorec
        if self.metronome_flash > 0:
            flash_intensity = int(255 * self.metronome_flash)
            click_color = (flash_intensity, flash_intensity, flash_intensity)
            pygame.draw.rect(self.screen, click_color, pygame.Rect(x + 40, y - 10, 16, 20))
            self.metronome_flash -= 0.1
        else:
            pygame.draw.rect(self.screen, (60, 60, 60), pygame.Rect(x + 40, y - 10, 16, 20), 1)

        # Hlavný kruh
        pygame.draw.circle(self.screen, base_color, (x, y), radius, 3)

        # Metronómové vlny
        for i in range(1, 4):
            wave_radius = radius + i * 12 + (beat_progress * 20)
            alpha = max(0, 255 - i * 80)

            wave_color = (base_color[0], base_color[1], base_color[2], alpha)
            wave_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, wave_color, (x, y), int(wave_radius), 2)
            self.screen.blit(wave_surface, (0, 0))

        # Stabilita ako číslo
        stability_text = f"Stability: {self.stability * 100:.0f}%"
        stability_surface = self.small_font.render(stability_text, True, (200, 200, 200))
        self.screen.blit(stability_surface, (10, 40))

    # ---------------------------------------------------------
    # BPM HISTORY GRAF
    # ---------------------------------------------------------
    def draw_bpm_history(self):
        if not self.bpm_history:
            return

        graph_width = 200
        graph_height = 60
        x = 10
        y = 70

        pygame.draw.rect(self.screen, (30, 30, 30), pygame.Rect(x, y, graph_width, graph_height))
        pygame.draw.rect(self.screen, (80, 80, 80), pygame.Rect(x, y, graph_width, graph_height), 1)

        min_bpm = min(self.bpm_history)
        max_bpm = max(self.bpm_history)
        if max_bpm == min_bpm:
            max_bpm += 1.0

        n = len(self.bpm_history)
        if n < 2:
            return

        step_x = graph_width / (n - 1)
        points = []

        for i, bpm in enumerate(self.bpm_history):
            norm = (bpm - min_bpm) / (max_bpm - min_bpm)
            px = x + i * step_x
            py = y + graph_height - norm * graph_height
            points.append((px, py))

        pygame.draw.lines(self.screen, (0, 200, 255), False, points, 2)

        label = f"History ({min_bpm:.0f}-{max_bpm:.0f} BPM)"
        label_surface = self.small_font.render(label, True, (180, 180, 180))
        self.screen.blit(label_surface, (x, y + graph_height + 2))

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        self.staff_ui.draw(self.screen)
        self.piano_ui.draw()
        self.screen.blit(self.piano_ui.screen, (0, 200))

        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 400))

        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        if self.bpm_value is not None:
            self.draw_bpm_visual()

        self.draw_bpm_history()

        pygame.display.flip()

    # ---------------------------------------------------------
    # HLAVNÁ SLUČKA UI
    # ---------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw()
            clock.tick(60)

        pygame.quit()
