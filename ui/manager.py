import pygame
from .piano_ui import PianoUI
from .piano_roll_ui import PianoRollUI
from .staff_ui import StaffUI
from .note_visualizer_ui import NoteVisualizerUI
from .track_switcher_ui import TrackSwitcherUI
from .canvas_ui import CanvasUI
from .transport_ui import TransportUI
from renderer.graphic_renderer import GraphicNotationRenderer


class UIManager:
    def __init__(self, width, height, track_system, notation_processor):
        self.width = width
        self.height = height
        self.track_system = track_system
        self.notation_processor = notation_processor

        pygame.font.init()

        self.transport = TransportUI(width, 50)
        self.is_playing = False
        self.play_start_time = 0
        self.current_time_ms = 0

        self.track_switcher = TrackSwitcherUI(
            x=0,
            y=55,
            width=width,
            height=60,
            track_colors=track_system.track_colors,
            event_bus=track_system.event_bus
        )

        self.piano = PianoUI(width, 180)
        self.piano_roll = PianoRollUI(width, 180)
        self.staff = StaffUI(width, 200)
        self.visualizer = NoteVisualizerUI(width, 200)

        self.active_track_id = 0

        self.track_activity = {}
        try:
            track_count = len(getattr(self.track_system, "tracks", {}))
        except Exception:
            track_count = 0

        for i in range(track_count):
            self.track_activity[i] = 0.0

        self.renderer = GraphicNotationRenderer(width, 200, track_system)
        if self.notation_processor is not None:
            try:
                self.notation_processor.bind_renderer(self.renderer)
            except Exception as e:
                print(f"❌ NotationProcessor bind_renderer error: {e}")

        self.canvas_ui = None
        self.canvas = None

        self.layout = {
            "transport": (0, 0),
            "track_switcher": (0, 55),
            "piano": (0, 130),
            "piano_roll": (0, 320),
            "staff": (0, 510),
            "visualizer": (0, 710),
            "renderer": (0, 920),
        }

    def build_layout(self, parent):
        self.canvas_ui = CanvasUI(parent)
        self.canvas = self.canvas_ui.get_canvas()

    def handle_event(self, event):
        t = self.transport.handle_event(event)
        if t:
            action = t.get("action")

            if action == "play":
                self.is_playing = True
                self.play_start_time = pygame.time.get_ticks() - self.current_time_ms

            elif action == "stop":
                self.is_playing = False
                self.current_time_ms = 0
                self.transport.set_time("00:00.0")

        if event.type == pygame.MOUSEBUTTONDOWN:
            try:
                self.track_switcher.handle_event(event)
            except Exception as e:
                print(f"❌ TrackSwitcherUI error: {e}")

    def on_note_on(self, event):
        if not isinstance(event, dict):
            return

        track_id = event.get("track_id", 0)
        note = event.get("note")
        if note is None:
            return

        velocity = event.get("velocity", 100)
        try:
            self.track_activity[track_id] = min(1.0, velocity / 127.0)
        except Exception:
            pass

        track_color = None
        if self.track_system is not None:
            try:
                track_color = self.track_system.get_color(track_id)
            except Exception:
                pass

        if track_color is not None:
            event["track_color"] = track_color

        try:
            self.piano.highlight_key(note, track_color)
        except Exception:
            pass

        try:
            self.piano_roll.highlight_key(note, track_color)
        except Exception:
            pass

        try:
            self.visualizer.on_note(event)
        except Exception:
            pass

        try:
            self.staff.add_note(event)
        except Exception:
            pass

        if self.notation_processor is not None:
            try:
                self.notation_processor.process_midi_event({
                    "type": "note_on",
                    "note": note,
                    "velocity": velocity,
                    "time": event.get("time", 0.0),
                    "channel": track_id,
                })
            except Exception:
                pass

    def on_note_off(self, event):
        if not isinstance(event, dict):
            return

        note = event.get("note")
        if note is None:
            return

        track_id = event.get("track_id", 0)

        try:
            self.track_activity[track_id] = 0.0
        except Exception:
            pass

        try:
            self.piano.unhighlight_key(note)
        except Exception:
            pass

        try:
            self.piano_roll.unhighlight_key(note)
        except Exception:
            pass

        try:
            self.visualizer.on_note_off(event)
        except Exception:
            pass

        try:
            self.staff.remove_note(event)
        except Exception:
            pass

        if self.notation_processor is not None:
            try:
                self.notation_processor.process_midi_event({
                    "type": "note_off",
                    "note": note,
                    "velocity": 0,
                    "time": event.get("time", 0.0),
                    "channel": track_id,
                })
            except Exception:
                pass

    def _fade_activity(self):
        try:
            for track_id in self.track_activity:
                self.track_activity[track_id] = max(0.0, self.track_activity[track_id] - 0.02)
        except Exception:
            pass

    def _update_time(self):
        if self.is_playing:
            self.current_time_ms = pygame.time.get_ticks() - self.play_start_time

            total_ms = self.current_time_ms
            seconds = (total_ms // 1000) % 60
            minutes = (total_ms // 60000)
            tenths = (total_ms % 1000) // 100

            time_str = f"{minutes:02}:{seconds:02}.{tenths}"
            self.transport.set_time(time_str)

    def draw(self, surface):
        self._fade_activity()
        self._update_time()

        try:
            x, y = self.layout["transport"]
            self.transport.draw(surface.subsurface((x, y, self.width, 50)))
        except Exception:
            pass

        try:
            x, y = self.layout["track_switcher"]
            self.track_switcher.draw(surface.subsurface((x, y, self.width, 60)))
        except Exception:
            pass

        try:
            x, y = self.layout["piano"]
            self.piano.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception:
            pass

        try:
            x, y = self.layout["piano_roll"]
            self.piano_roll.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception:
            pass

        try:
            x, y = self.layout["staff"]
            self.staff.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass

        try:
            x, y = self.layout["visualizer"]
            self.visualizer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass

        try:
            x, y = self.layout["renderer"]
            self.renderer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass
