import pygame
from .piano_ui import PianoUI
from .piano_roll_ui import PianoRollUI
from .staff_ui import StaffUI
from .note_visualizer_ui import NoteVisualizerUI
from .track_selector_ui import TrackSelectorUI
from .canvas_ui import CanvasUI
from renderer.graphic_renderer import GraphicNotationRenderer


class UIManager:
    def __init__(self, width, height, track_system, notation_processor):
        self.width = width
        self.height = height
        self.track_system = track_system
        self.notation_processor = notation_processor

        pygame.font.init()

        self.piano = PianoUI(width, 180)
        self.piano_roll = PianoRollUI(width, 180)
        self.staff = StaffUI(width, 200)
        self.visualizer = NoteVisualizerUI(width, 200)
        self.track_selector = TrackSelectorUI(track_system, width=width, height=60)

        self.active_track_id = 0

        self.renderer = GraphicNotationRenderer(width, 200, track_system)
        if self.notation_processor is not None:
            try:
                self.notation_processor.bind_renderer(self.renderer)
            except Exception as e:
                print(f"❌ NotationProcessor bind_renderer error: {e}")

        self.canvas_ui = None
        self.canvas = None

        self.layout = {
            "track_selector": (0, 0),
            "piano": (0, 70),
            "piano_roll": (0, 260),
            "staff": (0, 450),
            "visualizer": (0, 650),
            "renderer": (0, 860),
        }

    def build_layout(self, parent):
        self.canvas_ui = CanvasUI(parent)
        self.canvas = self.canvas_ui.get_canvas()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.track_selector:
            try:
                clicked_track = self.track_selector.handle_click(event.pos)
                if clicked_track is not None:
                    self.active_track_id = clicked_track
            except Exception as e:
                print(f"❌ TrackSelector handle_click error: {e}")

    def on_note_on(self, event):
        if not isinstance(event, dict):
            return

        track_id = event.get("track_id", 0)
        note = event.get("note")
        if note is None:
            return

        track_color = None
        if self.track_system is not None:
            try:
                track_color = self.track_system.get_color(track_id)
            except Exception as e:
                print(f"❌ TrackSystem get_color error: {e}")

        if track_color is not None:
            event["track_color"] = track_color

        try:
            if self.piano:
                self.piano.highlight_key(note, track_color)
        except Exception as e:
            print(f"❌ PianoUI highlight_key error: {e}")

        try:
            if self.piano_roll:
                self.piano_roll.highlight_key(note, track_color)
        except Exception as e:
            print(f"❌ PianoRollUI highlight_key error: {e}")

        try:
            if self.visualizer:
                self.visualizer.on_note(event)
        except Exception as e:
            print(f"❌ NoteVisualizerUI on_note error: {e}")

        try:
            if self.staff:
                self.staff.add_note(event)
        except Exception as e:
            print(f"❌ StaffUI add_note error: {e}")

        if self.notation_processor is not None:
            try:
                self.notation_processor.process_midi_event({
                    "type": "note_on",
                    "note": note,
                    "velocity": event.get("velocity", 100),
                    "time": event.get("time", 0.0),
                    "channel": track_id,
                })
            except Exception as e:
                print(f"❌ NotationProcessor process_midi_event (note_on) error: {e}")

    def on_note_off(self, event):
        if not isinstance(event, dict):
            return

        note = event.get("note")
        if note is None:
            return

        track_id = event.get("track_id", 0)

        try:
            if self.piano:
                self.piano.unhighlight_key(note)
        except Exception as e:
            print(f"❌ PianoUI unhighlight_key error: {e}")

        try:
            if self.piano_roll:
                self.piano_roll.unhighlight_key(note)
        except Exception as e:
            print(f"❌ PianoRollUI unhighlight_key error: {e}")

        try:
            if self.visualizer:
                self.visualizer.on_note_off(event)
        except Exception as e:
            print(f"❌ NoteVisualizerUI on_note_off error: {e}")

        try:
            if self.staff:
                self.staff.remove_note(event)
        except Exception as e:
            print(f"❌ StaffUI remove_note error: {e}")

        if self.notation_processor is not None:
            try:
                self.notation_processor.process_midi_event({
                    "type": "note_off",
                    "note": note,
                    "velocity": 0,
                    "time": event.get("time", 0.0),
                    "channel": track_id,
                })
            except Exception as e:
                print(f"❌ NotationProcessor process_midi_event (note_off) error: {e}")

    def draw(self, surface):
        try:
            x, y = self.layout["track_selector"]
            if self.track_selector:
                self.track_selector.draw(
                    surface.subsurface((x, y, self.width, 60)),
                    active_track=self.active_track_id
                )
        except Exception as e:
            print(f"❌ TrackSelector draw error: {e}")

        try:
            x, y = self.layout["piano"]
            if self.piano:
                self.piano.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception as e:
            print(f"❌ PianoUI draw error: {e}")

        try:
            x, y = self.layout["piano_roll"]
            if self.piano_roll:
                self.piano_roll.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception as e:
            print(f"❌ PianoRollUI draw error: {e}")

        try:
            x, y = self.layout["staff"]
            if self.staff:
                self.staff.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception as e:
            print(f"❌ StaffUI draw error: {e}")

        try:
            x, y = self.layout["visualizer"]
            if self.visualizer:
                self.visualizer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception as e:
            print(f"❌ NoteVisualizerUI draw error: {e}")

        try:
            x, y = self.layout["renderer"]
            if self.renderer:
                self.renderer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception as e:
            print(f"❌ GraphicNotationRenderer draw error: {e}")
