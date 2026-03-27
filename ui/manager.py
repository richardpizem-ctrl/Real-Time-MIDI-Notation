import pygame
import time

from ui.staff_ui import StaffUI
from ui.piano_roll_ui import PianoRollUI
from ui.note_visualizer_ui import NoteVisualizerUI

from renderer.graphic_renderer import GraphicNotationRenderer
from performance.performance_tracker import PerformanceTracker


class UIManager:
    def __init__(
        self,
        width=1400,
        height=800,
        event_router=None,
        stream_handler=None,
        track_system=None
    ):
        pygame.init()

        self.width = width
        self.height = height

        # Hlavné okno
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation")

        # UI komponenty
        self.staff_ui = StaffUI(width, 200)                 # 0–200
        self.renderer = GraphicNotationRenderer(width, 200) # 200–400
        self.piano_ui = PianoRollUI(width, 200)             # 400–600
        self.note_visualizer = NoteVisualizerUI(width, 200) # 600–800

        # Externé moduly (prichádzajú z run.py)
        self.event_router = event_router
        self.stream_handler = stream_handler
        self.track_system = track_system

        # Performance tracker
        self.perf = PerformanceTracker()
        self.performance_stats = {}

        # Fonty
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)

        # Debug mode
        self.debug_mode = True

        # BPM / rytmická vizualizácia
        self.last_beat_index = 0
        self.beats_per_bar = 4
        self.metronome_flash = 0.0


    # ---------------------------------------------------------
    # UPDATE LOOP – Performance Tracker + BPM pulz + UI
    # ---------------------------------------------------------
    def update(self):
        # 1) Získanie metrík
        self.performance_stats = self.perf.get_metrics()

        bpm = self.performance_stats.get("bpm")
        now = time.time()

        # 2) BPM pulz
        self.note_visualizer.update_bpm_pulse(bpm, now)
        self.renderer.update_bpm_pulse(bpm, now)

        # 3) Downbeat flash
        if bpm and bpm > 0:
            beats_per_sec = bpm / 60.0
            beat_pos = now * beats_per_sec
            beat_index = int(beat_pos) % self.beats_per_bar

            if beat_index == 0 and self.last_beat_index != 0:
                self.metronome_flash = 1.0

            self.last_beat_index = beat_index
            self.metronome_flash *= 0.88
        else:
            self.metronome_flash = 0.0

        # 4) Update UI komponentov
        self.piano_ui.update(self.performance_stats)
        self.note_visualizer.update(self.performance_stats)
        self.renderer.update_performance(self.performance_stats)


    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        # 1) Notová osnova
        self.staff_ui.draw(self.screen)

        # 2) Grafický renderer
        renderer_surface = self.renderer.render()
        self.screen.blit(renderer_surface, (0, 200))

        # 3) Piano roll
        piano_surface = pygame.Surface((self.width, 200))
        self.piano_ui.draw(piano_surface)
        self.screen.blit(piano_surface, (0, 400))

        # 4) Note visualizer
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 600))

        # Downbeat flash
        if self.metronome_flash > 0.01:
            alpha = int(140 * max(0.0, min(1.0, self.metronome_flash)))
            flash_surface = pygame.Surface((self.width, 200), pygame.SRCALPHA)
            flash_surface.fill((255, 255, 255, alpha))

            self.screen.blit(flash_surface, (0, 200))
            self.screen.blit(flash_surface, (0, 600))

        # Debug text
        if self.debug_mode:
            latency = self.performance_stats.get("latency", 0)
            accuracy = self.performance_stats.get("accuracy", 0)
            bpm = self.performance_stats.get("bpm", 0)

            debug_text = [
                f
