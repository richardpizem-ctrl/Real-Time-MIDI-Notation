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
    def __init__(self, width=1400, height=600):
        pygame.init()
        self.width = width
        self.height = height

        # Hlavné okno
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation")

        # UI komponenty
        self.staff_ui = StaffUI(width, 200)
        self.renderer = GraphicNotationRenderer(width, 200)
        self.piano_ui = PianoRollUI(width, 200)
        self.note_visualizer = NoteVisualizerUI(width, 200)

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

        # 4) Note visualizer (voliteľné)
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)

        # BPM text
        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # Aktívny track
        active_track = self.track_system.get_active_track()
        if active_track is not None:
            track_text = f"Track {active_track.id}: {active_track.name} (CH {active_track.channel})"
            color = getattr(active_track, "color", (200, 200, 200))
            track_surface = self.small_font.render(track_text, True, color)
            self.screen.blit(track_surface, (300, 10))

        # BPM vizualizácia
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

            # Renderer spracuje eventy až po event loope
            self.renderer.run_event_loop_step()

            self.draw()
            clock.tick(60)

        pygame.quit()
