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
        self.debug_overlay = False  # fullscreen overlay

        # História FPS / CPU / Latency pre mini grafy
        self.fps_history = []
        self.cpu_history = []
        self.latency_history = []
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

        # Fullscreen debug overlay (F4)
        if self.debug_overlay:
            self.draw_debug_overlay()

        pygame.display.flip()

    # ---------------------------------------------------------
    # PERFORMANCE PANEL (oddelený box + mini grafy)
    # ---------------------------------------------------------
    def draw_performance_panel(self):
        panel_x = self.width - 280
        panel_y = 50
        panel_w = 260
        panel_h = 150

        # Pozadie panelu
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (200, 200, 200), (panel_x, panel_y, panel_w, panel_h), 2)

        fps = self.perf.get_fps()
        cpu = self.perf.get_cpu_load()
        latency = self.perf.get_event_latency()

        # Uloženie do histórie
        self.fps_history.append(fps)
        self.cpu_history.append(cpu)
        self.latency_history.append(latency)
        if len(self.fps_history) > self.max_perf_history:
            self.fps_history.pop(0)
        if len(self.cpu_history) > self.max_perf_history:
            self.cpu_history.pop(0)
        if len(self.latency_history) > self.max_perf_history:
            self.latency_history.pop(0)

        # Farebné zvýraznenie pri vysokom CPU
        if cpu >= 90:
            cpu_color = (255, 80, 80)
        elif cpu >= 70:
            cpu_color = (255, 180, 80)
        else:
            cpu_color = (220, 220, 220)

        # Farebné zvýraznenie pri vysokej latencii
        if latency >= 25:
            lat_color = (255, 80, 80)
        elif latency >= 10:
            lat_color = (255, 200, 80)
        else:
            lat_color = (220, 220, 220)

        # Textové metriky
        fps_text = f"FPS: {fps:.1f}"
        cpu_text = f"CPU: {cpu:.1f}%"
        lat_text = f"Latency: {latency:.2f} ms"

        fps_surf = self.font.render(fps_text, True, (220, 220, 220))
        cpu_surf = self.font.render(cpu_text, True, cpu_color)
        lat_surf = self.font.render(lat_text, True, lat_color)

        self.screen.blit(fps_surf, (panel_x + 10, panel_y + 8))
        self.screen.blit(cpu_surf, (panel_x + 10, panel_y + 8 + 24))
        self.screen.blit(lat_surf, (panel_x + 10, panel_y + 8 + 48))

        # Mini graf FPS
        self.draw_perf_graph(
            history=self.fps_history,
            x=panel_x + 10,
            y=panel_y + 8 + 72,
            w=panel_w - 20,
            h=18,
            color=(0, 200, 255),
            label="FPS"
        )

        # Mini graf CPU
        self.draw_perf_graph(
            history=self.cpu_history,
            x=panel_x + 10,
            y=panel_y + 8 + 72 + 22,
            w=panel_w - 20,
            h=18,
            color=cpu_color,
            label="CPU"
        )

        # Mini graf Latency
        self.draw_perf_graph(
            history=self.latency_history,
            x=panel_x + 10,
            y=panel_y + 8 + 72 + 44,
            w=panel_w - 20,
            h=18,
            color=lat_color,
            label="LAT"
        )

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
    # FULLSCREEN DEBUG OVERLAY
    # ---------------------------------------------------------
    def draw_debug_overlay(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("DEBUG PERFORMANCE OVERLAY", True, (255, 255, 255))
        self.screen.blit(title, (40, 30))

        box_x = 40
        box_y = 80
        box_w = self.width - 80
        box_h = self.height - 140
        pygame.draw.rect(self.screen, (30, 30, 30), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(self.screen, (200, 200, 200), (box_x, box_y, box_w, box_h), 2)

        # tri veľké grafy: FPS, CPU, Latency
        graph_h = (box_h - 60) // 3
        margin = 10

        self.draw_perf_graph(
            history=self.fps_history,
            x=box_x + margin,
            y=box_y + margin,
            w=box_w - 2 * margin,
            h=graph_h,
            color=(0, 200, 255),
            label="FPS"
        )

        self.draw_perf_graph(
            history=self.cpu_history,
            x=box_x + margin,
            y=box_y + margin + graph_h + 10,
            w=box_w - 2 * margin,
            h=graph_h,
            color=(255, 200, 80),
            label="CPU"
        )

        self.draw_perf_graph(
            history=self.latency_history,
            x=box_x + margin,
            y=box_y + margin + 2 * (graph_h + 10),
            w=box_w - 2 * margin,
            h=graph_h,
            color=(255, 120, 120),
            label="LATENCY (ms)"
        )

        hint = self.small_font.render("F4 – toggle overlay, F3 – toggle panel", True, (220, 220, 220))
        self.screen.blit(hint, (box_x + 10, box_y + box_h - 25))

    # ---------------------------------------------------------
    # JEMNEJŠIA BPM VIZUALIZÁCIA
    # ---------------------------------------------------------
    def draw_bpm_visual(self):
        center_x = self.width - 150
        center_y = 80

        base_radius = 20
        bpm_factor = min(max(self.bpm_value / 120.0, 0.5), 2.0)
        radius = int(base_radius * bpm_factor)

        self.breath_phase += 0.05
        breath = (math.sin(self.breath_phase) + 1) / 2
        radius += int(5 * breath)

        stability_clamped = max(0.0, min(self.stability, 1.0))
        r = int(255 * (1.0 - stability_clamped))
        g = int(255 * stability_clamped)
        b = 80

        pygame.draw.circle(self.screen, (r, g, b), (center_x, center_y), radius, 0)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius, 2)

        bpm_text = f"{int(self.bpm_value)}"
        bpm_surface = self.font_big.render(bpm_text, True, (255, 255, 255))
        text_rect = bpm_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(bpm_surface, text_rect)

    def draw_bpm_history(self):
        if not self.bpm_history:
            return

        graph_x = 10
        graph_y = 120
        graph_width = 260
        graph_height = 60

        pygame.draw.rect(self.screen, (80, 80, 80), (graph_x, graph_y, graph_width, graph_height), 1)

        min_bpm = min(self.bpm_history)
        max_bpm = max(self.bpm_history)
        if max_bpm == min_bpm:
            max_bpm += 1

        n = len(self.bpm_history)
        if n < 2:
            return

        step_x = graph_width / (n - 1)
        points = []
        for i, bpm in enumerate(self.bpm_history):
            x = graph_x + i * step_x
            norm = (bpm - min_bpm) / (max_bpm - min_bpm)
            y = graph_y + graph_height - norm * graph_height
            points.append((x, y))

        if len(points) >= 2:
            pygame.draw.lines(self.screen, (0, 200, 255), False, points, 2)

    # ---------------------------------------------------------
    # HLAVNÁ SLUČKA UI
    # ---------------------------------------------------------
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            self.perf.start_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # prepínanie debug panelu (F3)
                    if event.key == pygame.K_F3:
                        self.debug_mode = not self.debug_mode

                    # prepínanie fullscreen overlay (F4)
                    if event.key == pygame.K_F4:
                        self.debug_overlay = not self.debug_overlay

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

            self.perf.end_frame()
            clock.tick(60)

        pygame.quit()
