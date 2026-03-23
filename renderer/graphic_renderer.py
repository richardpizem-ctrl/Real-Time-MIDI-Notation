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
    - bubnové noteheady (X, diamond, open hat, ghost)
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

        # 🔥 ZOOM faktor
        self.zoom = 1.0

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
        y_top *= self.zoom
        spacing = self.staff_spacing * self.zoom

        for i in range(5):
            y = y_top + i * spacing
            pygame.draw.line(
                self.screen,
                self.staff_color,
                (40 * self.zoom, y),
                (self.width * self.zoom - 40 * self.zoom, y),
                int(2 * self.zoom)
            )

    def _draw_all_staffs(self):
        self._draw_staff(self.staff_top)
        self._draw_staff(self.bass_staff_top)

        # drums – jedna čiara
        pygame.draw.line(
            self.screen,
            self.staff_color,
            (40 * self.zoom, self.drums_y * self.zoom),
            (self.width * self.zoom - 40 * self.zoom, self.drums_y * self.zoom),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Vykreslenie taktovej čiary
    # ---------------------------------------------------------
    def _draw_barline(self, x):
        x = int(x * self.zoom)
        pygame.draw.line(
            self.screen,
            (180, 180, 180),
            (x, (self.staff_top - 10) * self.zoom),
            (x, (self.drums_y + 20) * self.zoom),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Vykreslenie bubnovej hlavičky
    # ---------------------------------------------------------
    def _draw_drum_notehead(self, x, y, drum):
        x = int(x * self.zoom)
        y = int(y * self.zoom)
        size = int(6 * self.zoom)

        head = drum["notehead_type"]

        # ghost → bledšia farba
        if drum["is_ghost"]:
            color = (180, 180, 180)
        else:
            color = (255, 150, 60)

        # X-head
        if head == "x":
            pygame.draw.line(self.screen, color, (x - size, y - size), (x + size, y + size), int(2 * self.zoom))
            pygame.draw.line(self.screen, color, (x - size, y + size), (x + size, y - size), int(2 * self.zoom))

            # open hat → malý kruh nad X
            if drum["is_open_hat"]:
                pygame.draw.circle(self.screen, color, (x, y - int(10 * self.zoom)), int(4 * self.zoom), int(1 * self.zoom))

        # diamond
        elif head == "diamond":
            pygame.draw.polygon(
                self.screen,
                color,
                [(x, y - size), (x + size, y), (x, y + size), (x - size, y)],
                int(2 * self.zoom)
            )

        # triangle (perkusie)
        elif head == "triangle":
            pygame.draw.polygon(
                self.screen,
                color,
                [(x, y - size), (x + size, y + size), (x - size, y + size)],
                int(2 * self.zoom)
            )

        # default → normálna nota
        else:
            pygame.draw.circle(self.screen, color, (x, y), size, int(2 * self.zoom))

    # ---------------------------------------------------------
    # Vykreslenie noty
    # ---------------------------------------------------------
    def _draw_note(self, note):
        x = int(note["x"] * self.zoom)
        y = int(note["y"] * self.zoom)
        track = note.get("track_type", "melody")

        # layering pre bicie
        if "drum_layer_offset" in note:
            x += int(note["drum_layer_offset"] * self.zoom)

        # bubny majú vlastné hlavičky
        if track == "drums" and "drum" in note:
            self._draw_drum_notehead(x, y, note["drum"])
            return

        # normálna nota
        color = self.track_colors.get(track, (255, 255, 255))
        pygame.draw.circle(self.screen, color, (x, y), int(6 * self.zoom))

    # ---------------------------------------------------------
    # Hlavné vykreslenie
    # ---------------------------------------------------------
    def render(self):
        dt = self.clock.tick(60) / 1000.0
        self.scroll_x += dt * self.scroll_speed

        self.screen.fill(self.background_color)

        # osnovy
        self._draw_all_staffs()

        # položky
        for item in self.items:
            base_x = item.get("x", 0)
            screen_x = (base_x - self.scroll_x)

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
