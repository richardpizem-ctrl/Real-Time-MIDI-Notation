import pygame
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
        # BPM LABEL + PULZUJÚCI KRUH
        # ---------------------------------------------------------
        self.font = pygame.font.SysFont("Arial", 28)
        self.current_bpm_text = "BPM: —"

        # Pulz kruhu
        self.bpm_pulse_radius = 20
        self.bpm_pulse_growth = 0
        self.bpm_last_value = None

    # ---------------------------------------------------------
    # API pre NotationProcessor
    # ---------------------------------------------------------
    def add_note_to_staff(self, note_id, x, y, color=None):
        self.staff_ui.add_note(note_id, x, y, color)

    def remove_note_from_staff(self, note_id):
        self.staff_ui.remove_note(note_id)

    def highlight_staff_note(self, note_id, color=None):
        self.staff_ui.highlight_note(note_id, color)

    def unhighlight_staff_note(self, note_id):
        self.staff_ui.unhighlight_note(note_id)

    def highlight_piano_key(self, midi_note, color=(255, 0, 0)):
        self.piano_ui.highlight_key(midi_note, color)

    def unhighlight_piano_key(self, midi_note):
        self.piano_ui.unhighlight_key(midi_note)

    def show_note_name(self, note_name, color=None):
        self.note_visualizer.set_note(note_name, color)

    def clear_note_name(self):
        self.note_visualizer.clear_note()

    # ---------------------------------------------------------
    # BPM UPDATE – text + pulz
    # ---------------------------------------------------------
    def update_bpm(self, bpm):
        """Aktualizuje BPM text aj pulz kruhu."""
        if bpm is None:
            self.current_bpm_text = "BPM: —"
            self.bpm_last_value = None
            return

        self.current_bpm_text = f"BPM: {bpm:.1f}"

        # Ak sa BPM zmenilo → spusti pulz
        if self.bpm_last_value != bpm:
            self.bpm_pulse_growth = 12  # sila pulzu
            self.bpm_last_value = bpm

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

        # ---------------------------------------------------------
        # BPM TEXT
        # ---------------------------------------------------------
        bpm_surface = self.font.render(self.current_bpm_text, True, (255, 255, 0))
        self.screen.blit(bpm_surface, (10, 10))

        # ---------------------------------------------------------
        # PULZUJÚCI BPM KRUH
        # ---------------------------------------------------------
        pulse_radius = self.bpm_pulse_radius + self.bpm_pulse_growth
        pygame.draw.circle(self.screen, (255, 200, 0), (120, 30), pulse_radius, 3)

        # postupné zmenšovanie pulzu
        if self.bpm_pulse_growth > 0:
            self.bpm_pulse_growth -= 0.8

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
