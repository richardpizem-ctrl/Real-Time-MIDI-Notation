import pygame


class GraphicNotationRenderer:
    """
    Jednoduchý grafický renderer:
    - otvorí okno
    - vykreslí päťčiarie
    - vykresľuje noty ako bodky na čiare
    """

    def __init__(self, width=1000, height=400):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.background_color = (20, 20, 20)
        self.staff_color = (220, 220, 220)
        self.note_color = (100, 200, 255)

        # uložené noty na vykreslenie
        self.notes = []

        # základné rozloženie
        self.staff_top = 100
        self.staff_spacing = 12  # vzdialenosť medzi čiarami
        self.note_spacing_x = 25  # horizontálny odstup medzi notami

        self._running = True

        # FPS kontrola
        self.clock = pygame.time.Clock()

    def add_note(self, note):
        """
        Očakáva dict s 'pitch' a 'bar'/'beat' (z NotationEngine).
        Zatiaľ len pridá notu do zoznamu a prekreslí obrazovku.
        """
        self.notes.append(note)
        self.render()

    def _pitch_to_y(self, pitch):
        """
        Veľmi jednoduché mapovanie pitch → vertikálna pozícia.
        Neskôr sa môže nahradiť reálnou notovou osnovou.
        """
        # middle C (60) niekde v strede päťčiarí
        base_pitch = 60
        offset = (pitch - base_pitch)
        return self.staff_top + 2 * self.staff_spacing - offset * 3

    def _draw_staff(self):
        for i in range(5):
            y = self.staff_top + i * self.staff_spacing
            pygame.draw.line(
                self.screen,
                self.staff_color,
                (50, y),
                (self.width - 50, y),
                2
            )

    def _draw_notes(self):
        x_start = 80
        for i, note in enumerate(self.notes):
            x = x_start + i * self.note_spacing_x
            y = self._pitch_to_y(note.get("pitch", 60))
            pygame.draw.circle(self.screen, self.note_color, (int(x), int(y)), 6)

    def render(self):
        self.screen.fill(self.background_color)
        self._draw_staff()
        self._draw_notes()
        pygame.display.flip()

        # FPS limit
        self.clock.tick(60)

    def run_event_loop_step(self):
        """
        Jednoduchý krok event loopu – treba volať pravidelne v hlavnom programe,
        aby okno reagovalo.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

    def is_running(self):
        return self._running
