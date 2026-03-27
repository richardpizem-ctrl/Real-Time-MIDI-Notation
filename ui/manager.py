import pygame
import math
import time

from ui.staff_ui import StaffUI
from ui.piano_roll_ui import PianoRollUI
from ui.note_visualizer_ui import NoteVisualizerUI

# MIDI routing
from real_time_processing.stream_handler import StreamHandler
from midi_input.event_router import EventRouter

# Track systém (16 MIDI stôp)
from tracks.track_manager import TrackSystem

# Grafický renderer
from renderer.graphic_renderer import GraphicNotationRenderer

# Performance tracker
from performance.performance_tracker import PerformanceTracker


class UIManager:
    def __init__(self, width=1400, height=800):
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

        # Track systém – 16 MIDI stôp
        self.track_system = TrackSystem(event_bus=None)

        # Event routing
        self.event_router = EventRouter(
            event_bus=None,
            piano_roll_ui=self.piano_ui,
            note_visualizer=self.note_visualizer
        )

        # Stream handler
        self.stream_handler = StreamHandler(piano_roll_ui=self.piano_ui)
        self.stream_handler.event_router = self.event_router

        # Performance tracker
        self.perf = PerformanceTracker()
        self.performance_stats = {}

        # Fonty
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_big = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)

        # Debug mode
        self.debug_mode = True

        # História FPS / CPU
        self.fps_history = []
        self.cpu_history = []
        self.pipeline_history = []
        self.max_perf_history = 60

        # BPM / rytmická vizualizácia
        self.current_bpm_text = "BPM: —"
        self.bpm_value = None
        self.last_bpm = None
        self.beat_interval = 1.0
        self.last_beat_time = time.time()
        self.stability = 1.0

        # Beat counter
        self.beat_counter = 1
        self.time_signature = (4, 4)
        self.beats_per_bar = 4

        # Subdivízie
        self.subdivisions = ["1", "e", "&", "a"]

        # Dýchanie kruhu
        self.breath_phase = 0.0

        # História BPM
        self.bpm_history = []
        self.max_history = 60

        # Metronóm klik
        self.metronome_flash = 0.0

        # Tempo warning
        self.tempo_warning = False
        self.warning_timer = 0.0

        # Farby pre tracky
        self.track_colors = [
            (255, 80, 80), (80, 255, 80), (80, 160, 255), (255, 200, 80),
            (255, 80, 200), (80, 255, 200), (200, 80, 255), (180, 180, 255),
            (255, 180, 180), (180, 255, 180), (255, 255, 80), (80, 255, 255),
            (255, 120, 120), (120, 255, 120), (120, 120, 255), (255, 255, 255),
        ]

    # ---------------------------------------------------------
    # UPDATE LOOP – Performance Tracker + BPM pulz + UI
    # ---------------------------------------------------------
    def update(self):
        # 1) Získanie metrík z Performance Trackeru
        self.performance_stats = self.perf.get_metrics()

        # 2) BPM pulz → NoteVisualizerUI + GraphicNotationRenderer
        bpm = self.performance_stats.get("bpm")
        now = time.time()
        self.note_visualizer.update_bpm_pulse(bpm, now)
        self.renderer.update_bpm_pulse(bpm, now)

        # 3) Odovzdanie metrík UI komponentom
        self.piano_ui.update(self.performance_stats)
        self.note_visualizer.update(self.performance_stats)
        self.renderer.update_performance(self.performance_stats)

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        # 1) Notová osnova (0–200)
        self.staff_ui.draw(self.screen)

        # 2) Grafický renderer (200–400)
        renderer_surface = self.renderer.render()
        self.screen.blit(renderer_surface, (0, 200))

        # 3) Piano roll (400–600)
        piano_surface = pygame.Surface((self.width, 200))
        self.piano_ui.draw(piano_surface)
        self.screen.blit(piano_surface, (0, 400))

        # 4) Note visualizer (600–800)
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 600))

        # Debug text – Performance Tracker
        if self.debug_mode:
            latency = self.performance_stats.get("latency", 0)
            accuracy = self.performance_stats.get("accuracy", 0)
            bpm = self.performance_stats.get("bpm", 0)

            debug_text = [
                f"Latency: {latency:.2f} ms",
                f"Accuracy: {accuracy:.1f} %",
                f"Detected BPM: {bpm}"
            ]

            y = 10
            for line in debug_text:
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (10, y))
                y += 22

        pygame.display.flip()
