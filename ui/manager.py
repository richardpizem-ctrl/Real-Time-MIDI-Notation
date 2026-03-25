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
        self.current_bpm_text = "BPM: —"

        # Pulz kruhu
        self.bpm_value = None
        self.last_beat_time = time.time()
        self.beat_interval = 1.0  # default (60 BPM)
        self.stability = 1.0  # 1 = stabilné, 0 = nestabilné

        # Dýchanie kruhu
        self.breath_phase = 0.0

    # ---------------------------------------------------------
    # BPM UPDATE – text + beat interval + stabilita
    # ---------------------------------------------------------
    def update_bpm(self, bpm):
        """Aktualizuje BPM text, beat interval a stabilitu."""
        if bpm is None:
            self.current_bpm_text = "BPM: —"
            self.bpm_value = None
            return

        # Text
        self.current_bpm_text = f"BPM: {bpm:.1f}"

        # Beat interval
        self.beat_interval = 60.0 / bpm
        self.bpm_value = bpm

        # Stabilita (čím menšia zmena, tým stabilnejšie)
        if hasattr(self, "last_bpm"):
            diff = abs(self.last_bpm - bpm)
            self.stability = max(0.0, min(1.0, 1.0 - diff / 10.0))
        self.last_bpm = bpm

    # ---------------------------------------------------------
    # KRESLENIE BPM VIZUALIZÁCIE
    # ---------------------------------------------------------
    def draw_bpm_visual(self):
        x, y = 120, 30

        # Farba podľa stability
        # stabilné = zelené, nestabilné = červené
        color = (
            int(255 * (1 - self.stability)),
            int(255 * self.stability),
            0
        )

        # Čas od posledného beatu
        now = time.time()
        beat_progress = (now - self.last_beat_time) / self.beat_interval

        # Ak prešiel beat → pulz
        if beat_progress >= 1.0:
            self.last_beat_time = now
            beat_progress = 0.0

        # Pulzujúci hlavný kruh
        base_radius = 20 + 10 * (1 - beat_progress)

        # Jemné dýchanie
        self.breath_phase += 0.05
        breathing = 3 * math.sin(self.breath_phase)

        # Konečný polomer
        radius = int(base_radius + breathing)

        # Hlavný kruh
        pygame.draw.circle(self.screen, color, (x, y), radius, 3)

        # ---------------------------------------------------------
        # Metronómové vlny (viac vrstiev)
        # ---------------------------------------------------------
        for i in range(1, 4):
            wave_radius = radius + i * 12 + (beat_progress * 20)
            alpha = max(0, 255 - i * 80)

            wave_color = (color[0], color[1], color[2], alpha)

            # Pygame nepodporuje alfa v draw.circle → riešime Surface
            wave_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, wave_color, (x, y), int(wave_radius), 2)
            self.screen.blit(wave_surface, (0, 0))

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        # Staff (vrch)
        self.staff_ui.draw(self.screen)

        # Piano roll (stred)
        self.piano_ui.draw()
        self.screen.blit(self.piano_ui.screen, (0, 200))

        # Note visualizer (dole)
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 400))

        # BPM text
        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # BPM vizualizácia
        if self.bpm_value is not None:
            self.draw_bpm_visual()

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
