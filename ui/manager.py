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

        # BPM / rytmická vizualizácia
        self.font = pygame.font.SysFont("Arial", 28)
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

        # Farby pre tracky (fallback, ak Track nemá vlastnú farbu)
        self.track_colors = [
            (255, 80, 80),
            (80, 255, 80),
            (80, 160, 255),
            (255, 200, 80),
            (255, 80, 200),
            (80, 255, 200),
            (200, 80, 255),
            (180, 180, 255),
            (255, 180, 180),
            (180, 255, 180),
            (255, 255, 80),
            (80, 255, 255),
            (255, 120, 120),
            (120, 255, 120),
            (120, 120, 255),
            (255, 255, 255),
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
        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # Aktívny track
        active_track = self.track_system.get_active_track()
        if active_track is not None:
            # ak má track vlastnú farbu, použijeme ju, inak fallback podľa id
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

        pygame.display.flip()

    # ---------------------------------------------------------
    # JEMNEJŠIA BPM VIZUALIZÁCIA
    # ---------------------------------------------------------
    def draw_bpm_visual(self):
        """
        Pulzujúci kruh podľa BPM + stabilita.
        """
        center_x = self.width - 150
        center_y = 80

        # základný polomer podľa BPM
        base_radius = 20
        bpm_factor = min(max(self.bpm_value / 120.0, 0.5), 2.0)
        radius = int(base_radius * bpm_factor)

        # dýchanie kruhu
        t = time.time()
        self.breath_phase += 0.05
        breath = (math.sin(self.breath_phase) + 1) / 2  # 0–1
        radius += int(5 * breath)

        # farba podľa stability
        # stabilita 1.0 = zelená, nižšia = viac do oranžovej/červenej
        stability_clamped = max(0.0, min(self.stability, 1.0))
        r = int(255 * (1.0 - stability_clamped))
        g = int(255 * stability_clamped)
        b = 80

        pygame.draw.circle(self.screen, (r, g, b), (center_x, center_y), radius, 0)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius, 2)

        # text BPM
        bpm_text = f"{int(self.bpm_value)}"
        bpm_surface = self.font.render(bpm_text, True, (255, 255, 255))
        text_rect = bpm_surface.get_rect(center=(center_x, center_y))
        self.screen.blit(bpm_surface, text_rect)

    def draw_bpm_history(self):
        """
        Jednoduchý graf BPM histórie v spodnej časti horného panelu.
        """
        if not self.bpm_history:
            return

        # oblasť grafu
        graph_x = 10
        graph_y = 120
        graph_width = 260
        graph_height = 60

        # rámik
        pygame.draw.rect(self.screen, (80, 80, 80), (graph_x, graph_y, graph_width, graph_height), 1)

        # rozsah BPM
        min_bpm = min(self.bpm_history)
        max_bpm = max(self.bpm_history)
        if max_bpm == min_bpm:
            max_bpm += 1  # aby sme sa vyhli deleniu nulou

        # body
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # prepínanie trackov – čísla 1–9
                if event.type == pygame.KEYDOWN:
                    # čísla 1–9 ako priame voľby tracku (ak TrackSystem niečo také podporuje)
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1  # 0–8
                        if hasattr(self.track_system, "set_active_track_index"):
                            self.track_system.set_active_track_index(index)

                    # šípky – next/prev track (ak existujú metódy)
                    if event.key == pygame.K_RIGHT:
                        if hasattr(self.track_system, "next_track"):
                            self.track_system.next_track()
                    if event.key == pygame.K_LEFT:
                        if hasattr(self.track_system, "previous_track"):
                            self.track_system.previous_track()

            # Renderer spracuje eventy až po event loope
            self.renderer.run_event_loop_step()

            self.draw()
            clock.tick(60)

        pygame.quit()
