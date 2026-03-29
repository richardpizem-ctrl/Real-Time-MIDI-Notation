import pygame
from .piano_ui import PianoUI
from .piano_roll_ui import PianoRollUI
from .staff_ui import StaffUI
from .note_visualizer_ui import NoteVisualizerUI
from .track_selector_ui import TrackSelectorUI
from renderer.graphic_renderer import GraphicNotationRenderer


class UIManager:
    def __init__(self, width, height, track_system):
        self.width = width
        self.height = height
        self.track_system = track_system

        pygame.font.init()

        # --- UI MODULY ---
        self.piano = PianoUI(width, 180)
        self.piano_roll = PianoRollUI(width, 180)
        self.staff = StaffUI(width, 200)
        self.visualizer = NoteVisualizerUI(width, 200)
        self.track_selector = TrackSelectorUI(track_system, width=width, height=60)

        # --- GRAPHIC NOTATION RENDERER ---
        self.renderer = GraphicNotationRenderer(width, 200, track_system)

        # Rozloženie UI
        self.layout = {
            "track_selector": (0, 0),
            "piano": (0, 70),
            "piano_roll": (0, 260),
            "staff": (0, 450),
            "visualizer": (0, 650),
            "renderer": (0, 860),
        }

        # Zoznam aktívnych nôt pre renderer
        self.active_notes = []


    # ---------------------------------------------------------
    # EVENT ROUTING
    # ---------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.track_selector.handle_click(event.pos)

    # ---------------------------------------------------------
    # NOTE ON / OFF
    # ---------------------------------------------------------
    def on_note_on(self, event):
        track_color = self.track_system.get_color(event["track_id"])
        event["track_color"] = track_color

        # UI reakcie
        self.piano.highlight_key(event["note"], track_color)
        self.piano_roll.highlight_key(event["note"], track_color)
        self.visualizer.on_note(event)
        self.staff.add_note(event)

        # Renderer notes
        self.active_notes.append(event)

    def on_note_off(self, event):
        self.piano.unhighlight_key(event["note"])
        self.piano_roll.unhighlight_key(event["note"])
        self.visualizer.on_note_off(event)
        self.staff.remove_note(event)

        # Odstránenie z rendereru
        self.active_notes = [
            n for n in self.active_notes
            if not (n["note"] == event["note"] and n["track_id"] == event["track_id"])
        ]

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # Track selector
        x, y = self.layout["track_selector"]
        self.track_selector.draw(surface.subsurface((x, y, self.width, 60)))

        # Piano
        x, y = self.layout["piano"]
        self.piano.draw(surface.subsurface((x, y, self.width, 180)))

        # Piano roll
        x, y = self.layout["piano_roll"]
        self.piano_roll.draw(surface.subsurface((x, y, self.width, 180)))

        # Staff
        x, y = self.layout["staff"]
        self.staff.draw(surface.subsurface((x, y, self.width, 200)))

        # Visualizer
        x, y = self.layout["visualizer"]
        self.visualizer.draw(surface.subsurface((x, y, self.width, 200)))

        # Renderer – kreslíme noty
        x, y = self.layout["renderer"]
        rendered = self.renderer.draw(self.active_notes)
        surface.subsurface((x, y, self.width, 200)).blit(rendered, (0, 0))
