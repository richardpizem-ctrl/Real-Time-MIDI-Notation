import pygame
from ui.staff_ui import StaffUI
from ui.piano_roll_ui import PianoRollUI
from ui.note_visualizer_ui import NoteVisualizerUI

# StreamHandler musí byť pripojený k UI
from real_time_processing.stream_handler import StreamHandler


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

        # 🔥 Prepojenie MIDI → StreamHandler → UI
        self.stream_handler = StreamHandler(piano_roll_ui=self.piano_ui)

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
    # KRESLENIE
    # ---------------------------------------------------------
    def draw(self):
        self.screen.fill((20, 20, 20))

        # Staff (vrch)
        self.staff_ui.draw(self.screen)

        # Piano roll (stred)
        piano_surface = pygame.Surface((self.width, 200))
        self.piano_ui.draw()  # kreslí do svojho vlastného surface
        piano_surface.blit(self.piano_ui.screen, (0, 0))
        self.screen.blit(piano_surface, (0, 200))

        # Note visualizer (dole)
        visual_surface = pygame.Surface((self.width, 200))
        self.note_visualizer.draw(visual_surface)
        self.screen.blit(visual_surface, (0, 400))

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

            # 🔥 UI sa prekreslí
            self.draw()

            clock.tick(60)

        pygame.quit()
