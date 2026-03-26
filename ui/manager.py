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
        self.event_router = EventRouter(event_bus=None, piano_roll_ui=self.piano_ui)
        self.stream_handler = StreamHandler(piano_roll_ui=self.piano_ui)
        self.stream_handler.event_router = self.event_router

        # Performance tracker
        self.perf = PerformanceTracker()
        self.font = pygame.font.SysFont("Arial", 20)

        # Debug mode (prepínanie panelu)
        self.debug_mode = True

        # História FPS / CPU pre mini grafy
        self.fps_history = []
        self.cpu_history = []
        self.pipeline_history = []
        self.max_perf_history = 60

        # BPM / rytmická vizualizácia
        self.font_big = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.current_bpm_text = "BPM: —"

        self.bpm_value = None
        self.last_bpm = None
        self.beat_interval = 1.0
        self.last_beat_time = time.time()
        self.stability = 1.0

        # Beat counter a takt
        self.beat_counter = 1
        self.time_signature = (4, 4)
        self.beats_per_bar = 4

        # Subdivízie (1 e & a)
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

        # BPM text
        bpm_surface = self.font_big.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # Aktívny track
        active_track = self.track_system.get_active_track()
        if active_track is not None:
            color = getattr(
                active_track,
                "color",
                self.track_colors[active_track.id % len(self.track_colors)],
            )
            track_text = f"Track {active_track.id}: {active_track.name} (CH {active_track.channel})"
            track_surface = self.small_font.render(track_text, True, color)
            self.screen.blit(track_surface, (300, 10))

        # BPM vizualizácia
        if self.bpm_value is not None:
            self.draw_bpm_visual()

        # História BPM
        self.draw_bpm_history()

        # Performance panel (len ak je debug_mode zapnutý)
        if self.debug_mode:
            self.draw_performance_panel()

        pygame.display.flip()

    # ---------------------------------------------------------
    # PERFORMANCE PANEL (oddelený box + mini grafy)
    # ---------------------------------------------------------
    def draw_performance_panel(self):
        summary = self.perf.get_summary()

        fps = summary["fps"]
        cpu = summary["cpu_percent"] or 0.0
        pipeline = summary["avg_pipeline_latency_ms"]

        # Uloženie do histórie
        self.fps_history.append(fps)
        self.cpu_history.append(cpu)
        self.pipeline_history.append(pipeline)

        if len(self.fps_history) > self.max_perf_history:
            self.fps_history.pop(0)
        if len(self.cpu_history) > self.max_perf_history:
            self.cpu_history.pop(0)
        if len(self.pipeline_history) > self.max_perf_history:
            self.pipeline_history.pop(0)

        panel_x = self.width - 280
        panel_y = 50
        panel_w = 260
        panel_h = 160

        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (200, 200, 200), (panel_x, panel_y, panel_w, panel_h), 2)

        # Textové metriky
        fps_surf = self.font.render(f"FPS: {fps:.1f}", True, (220, 220, 220))
        cpu_surf = self.font.render(f"CPU: {cpu:.1f}%", True, (255, 200, 80))
        lat_surf = self.font.render(f"Pipeline: {pipeline:.2f} ms", True, (220, 220, 220))

        self.screen.blit(fps_surf, (panel_x + 10, panel_y + 8))
        self.screen.blit(cpu_surf, (panel_x + 10, panel_y + 32))
        self.screen.blit(lat_surf, (panel_x + 10, panel_y + 56))

        # Mini grafy
        self.draw_perf_graph(self.fps_history, panel_x + 10, panel_y + 80, panel_w - 20, 18, (0, 200, 255), "FPS")
        self.draw_perf_graph(self.cpu_history, panel_x + 10, panel_y + 102, panel_w - 20, 18, (255, 200, 80), "CPU")
        self.draw_perf_graph(self.pipeline_history, panel_x + 10, panel_y + 124, panel_w - 20, 18, (255, 80, 80), "PIPE")

    def draw_perf_graph(self, history, x, y, w, h, color, label=None):
        if len(history) < 2:
            return

        pygame.draw.rect(self.screen, (50, 50, 50), (x, y, w, h))
        pygame.draw.rect(self.screen, (120, 120, 120), (x, y, w, h), 1)

        min_val = min(history)
        max_val = max(history)
        if max_val == min_val:
            max_val += 1.0

        n = len(history)
        step_x = w / (n - 1)
        points = []
        for i, val in enumerate(history):
            px = x + i * step_x
            norm = (val - min_val) / (max_val - min_val)
            py = y + h - norm * h
            points.append((px, py))

        if len(points) >= 2:
            pygame.draw.lines(self.screen, color, False, points, 2)

        if label:
            label_surf = self.small_font.render(label, True, (200, 200, 200))
            self.screen.blit(label_surf, (x + 4, y + 1))

    # ---------------------------------------------------------
    # HLAVNÁ SLUČKA UI
    # ---------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.perf.frame_start()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F3:
                        self.debug_mode = not self.debug_mode

                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if hasattr(self.track_system, "set_active_track_index"):
                            self.track_system.set_active_track_index(index)

                    if event.key == pygame.K_RIGHT:
                        if hasattr(self.track_system, "next_track"):
                            self.track_system.next_track()
                    if event.key == pygame.K_LEFT:
                        if hasattr(self.track_system, "previous_track"):
                            self.track_system.previous_track()

            self.renderer.run_event_loop_step()
            self.draw()

            self.perf.frame_end()
            clock.tick(60)

        pygame.quit()
