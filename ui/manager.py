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

        # Track systém – 16 MIDI stôp
        self.track_system = TrackSystem(event_bus=None)

        # Event routing
        self.event_router = EventRouter(event_bus=None, piano_roll_ui=self.piano_ui)
        self.stream_handler = StreamHandler(piano_roll_ui=self.piano_ui)
        self.stream_handler.event_router = self.event_router

        # ---------------------------------------------------------
        # BPM / rytmická vizualizácia
        # ---------------------------------------------------------
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

        # Tempo warning (napr. BPM > 180)
        if bpm > 180:
            self.tempo_warning = True
            self.warning_timer = 1.0

    # ---------------------------------------------------------
    # BPM VIZUALIZÁCIA + takt + subdivízie + pendulum
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

        # Nový beat
        if beat_progress >= 1.0:
            self.last_beat_time = now
            beat_progress = 0.0
            self.metronome_flash = 1.0

            # Beat counter podľa taktu
            self.beat_counter += 1
            if self.beat_counter > self.beats_per_bar:
                self.beat_counter = 1

        # Pulzujúci hlavný kruh
        base_radius = 20 + 10 * (1 - beat_progress)

        # Jemné dýchanie
        self.breath_phase += 0.05
        breathing = 3 * math.sin(self.breath_phase)

        radius = int(base_radius + breathing)

        # Accent beat (silný prvý beat v takte)
        if self.beat_counter == 1:
            accent_color = (255, 220, 120)
            pygame.draw.circle(self.screen, accent_color, (x, y), radius + 4, 4)

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

        # Beat counter
        beat_text = f"Beat: {self.beat_counter}"
        beat_surface = self.small_font.render(beat_text, True, (255, 255, 255))
        self.screen.blit(beat_surface, (10, 60))

        # Taktový meter
        ts_text = f"TS: {self.time_signature[0]}/{self.time_signature[1]}"
        ts_surface = self.small_font.render(ts_text, True, (180, 180, 180))
        self.screen.blit(ts_surface, (10, 80))

        # Subdivízie (1 e & a)
        if self.subdivisions and self.beat_interval > 0:
            sub_count = len(self.subdivisions)
            sub_index = int(beat_progress * sub_count)
            if sub_index >= sub_count:
                sub_index = sub_count - 1
            subdiv_label = self.subdivisions[sub_index]
            subdiv_text = f"Subdiv: {subdiv_label}"
            subdiv_surface = self.small_font.render(subdiv_text, True, (200, 200, 255))
            self.screen.blit(subdiv_surface, (10, 100))

        # Tempo warning
        if self.tempo_warning:
            warning_color = (255, 50, 50)
            warning_surface = self.small_font.render("WARNING: HIGH TEMPO!", True, warning_color)
            self.screen.blit(warning_surface, (10, 120))
            self.warning_timer -= 0.02
            if self.warning_timer <= 0:
                self.tempo_warning = False

        # Vizuálny „pendulum“ metronóm
        if self.bpm_value is not None and self.beat_interval > 0:
            pendulum_origin = (x + 80, y + 40)
            length = 40
            max_angle = math.radians(35)

            omega = math.pi / self.beat_interval
            angle = math.sin(now * omega) * max_angle

            end_x = pendulum_origin[0] + length * math.sin(angle)
            end_y = pendulum_origin[1] + length * math.cos(angle)

            pygame.draw.line(self.screen, (220, 220, 220), pendulum_origin, (end_x, end_y), 3)
            pygame.draw.circle(self.screen, (240, 240, 240), (int(end_x), int(end_y)), 6)

    # ---------------------------------------------------------
    # BPM HISTORY GRAF
    # ---------------------------------------------------------
    def draw_bpm_history(self):
        if not self.bpm_history:
            return

        graph_width = 200
        graph_height = 60
        x = 10
        y = 160

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

    # ---------------------------------------------------------
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        # Notová osnova
        self.staff_ui.draw(self.screen)

        # Piano roll
        self.piano_ui.draw()
        self.screen.blit(self.piano_ui.screen, (0, 200))

        # Note visualizer
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 400))

        # BPM text
        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # Aktívny track – názov + kanál + farba
        active_track = self.track_system.get_active_track()
        if active_track is not None:
            track_text = f"Track {active_track.id}: {active_track.name} (CH {active_track.channel})"
            color = active_track.color if hasattr(active_track, "color") else (200, 200, 200)
            track_surface = self.small_font.render(track_text, True, color)
            self.screen.blit(track_surface, (300, 10))

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
