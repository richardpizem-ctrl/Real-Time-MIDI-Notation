import pygame


class GraphicNotationRenderer:
    """
    Jednoduchý grafický renderer pre real-time MIDI notáciu.
    Podporuje:
    - päťčiarie
    - basovú osnovu
    - bubnový grid
    - taktové čiary
    - farby podľa stopy
    - x/y pozície z PixelLayoutEngine
    - real-time horizontálny scrolling
    """

    def __init__(self, width=1200, height=500):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Real-Time MIDI Notation")

        self.background_color = (20, 20, 20)
        self.staff_color = (200, 200, 200)

        # farby podľa stopy
        self.track_colors = {
            "melody": (80, 160, 255),
            "bass": (120, 220, 120),
            "drums": (255, 150, 60),
        }

        # uložené prvky
        self.items = []

        # rozloženie
        self.staff_top = 80
        self.staff_spacing = 12
        self.bass_staff_top = 80 + 140
        self.drums_y = 80 + 140 + 80

        # scrolling
        self.scroll_x = 0.0
        self.scroll_speed = 40.0  # px/s

        self._running = True
        self.clock = pygame.time.Clock()

    # ---------------------------------------------------------
    # API pre NotationProcessor
    # ---------------------------------------------------------
    def add_note(self, note):
        self.items.append(note)
        self.render()

    def add_barline(self, x):
        self.items.append({"type": "barline", "x": x})
        self.render()

    # ---------------------------------------------------------
    # Vykresľovanie osnov
    # ---------------------------------------------------------
    def _draw_staff(self, y_top):
        for i in range(5):
            y = y_top + i * self.staff_spacing
            pygame.draw.line(
                self.screen,
                self.staff_color,
                (40, y),
                (self.width - 40, y),
                2
            )

    def _draw_all_staffs(self):
        self._draw_staff(self.staff_top)
        self._draw_staff(self.bass_staff_top)

        # drums – jedna čiara
        pygame.draw.line(
            self.screen,
            self.staff_color,
            (40, self.drums_y),
            (self.width - 40, self.drums_y),
            2
        )

    # ---------------------------------------------------------
    # Vykreslenie taktovej čiary
    # ---------------------------------------------------------
    def _draw_barline(self, x):
        x = int(x)
        pygame.draw.line(
            self.screen,
            (180, 180, 180),
            (x, self.staff_top - 10),
            (x, self.drums_y + 20),
            2
        )

    # ---------------------------------------------------------
    # Vykreslenie noty
    # ---------------------------------------------------------
    def _draw_note(self, note):
        x = int(note["x"])
        y = int(note["y"])
        track = note.get("track_type", "melody")

        color = self.track_colors.get(track, (255, 255, 255))
        pygame.draw.circle(self.screen, color, (x, y), 6)

    # ---------------------------------------------------------
    # Hlavné vykreslenie
    # ---------------------------------------------------------
    def render(self):
        # delta time
        dt = self.clock.tick(60) / 1000.0
        self.scroll_x += dt * self.scroll_speed

        self.screen.fill(self.background_color)

        # osnovy
        self._draw_all_staffs()

        # položky
        for item in self.items:
            # posun podľa scrollu
            base_x = item.get("x", 0)
            screen_x = base_x - self.scroll_x

            # ignoruj mimo obrazovky
            if screen_x < -100 or screen_x > self.width + 100:
                continue

            if item.get("type") == "barline":
                self._draw_barline(screen_x)
            else:
                shifted = dict(item)
                shifted["x"] = screen_x
                self._draw_note(shifted)

        pygame.display.flip()

    # ---------------------------------------------------------
    # Event loop
    # ---------------------------------------------------------
    def run_event_loop_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False

    def is_running(self):
        return self._running
