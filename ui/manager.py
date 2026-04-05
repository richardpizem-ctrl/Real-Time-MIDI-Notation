import pygame
from .piano_ui import PianoUI
from .piano_roll_ui import PianoRollUI
from .staff_ui import StaffUI
from .note_visualizer_ui import NoteVisualizerUI
from .track_switcher_ui import TrackSwitcherUI
from .canvas_ui import CanvasUI
from .transport_ui import TransportUI
from renderer.graphic_renderer import GraphicNotationRenderer
from renderer.exporter import export_to_png


class UIManager:
    def __init__(self, width, height, track_system, notation_processor):
        self.width = width
        self.height = height
        self.track_system = track_system
        self.notation_processor = notation_processor

        pygame.font.init()

        # TRANSPORT
        self.transport = TransportUI(width, 50)
        self.is_playing = False
        self.play_start_time = 0
        self.current_time_ms = 0

        # TRACK SWITCHER
        self.track_switcher = TrackSwitcherUI(
            x=0,
            y=55,
            width=width,
            height=60,
            track_colors=track_system.track_colors,
            event_bus=track_system.event_bus
        )

        # TRACK VISIBILITY
        self.track_visibility = {i: True for i in range(16)}

        track_system.event_bus.subscribe("track_toggle", self._on_track_toggle)
        track_system.event_bus.subscribe("track_selected", self._on_track_selected)
        track_system.event_bus.subscribe("track_mute", self._on_track_mute)
        track_system.event_bus.subscribe("track_solo", self._on_track_solo)

        # UI PANELS
        self.piano = PianoUI(width, 180)
        self.piano_roll = PianoRollUI(width, 180)
        self.staff = StaffUI(width, 200)
        self.visualizer = NoteVisualizerUI(width, 200)

        self.active_track_id = 0  # 0-based index pre UI / renderer

        # RENDERER
        self.renderer = GraphicNotationRenderer(width, 200, track_system)
        self._rebuild_track_visibility()

        if self.notation_processor is not None:
            try:
                self.notation_processor.bind_renderer(self.renderer)
            except Exception as e:
                print(f"❌ NotationProcessor bind_renderer error: {e}")

        # CANVAS / EXPORT
        self.canvas_ui = None
        self.canvas = None

        # Quantization state
        self.quantize_division = 1.0
        self.swing_amount = 0.0

        # Layout
        self.layout = {
            "transport": (0, 0),
            "track_switcher": (0, 55),
            "piano": (0, 130),
            "piano_roll": (0, 320),
            "staff": (0, 510),
            "visualizer": (0, 710),
            "renderer": (0, 920),
        }

        self.export_button_rect = pygame.Rect(self.width - 120, 10, 110, 35)
        self.export_font = pygame.font.SysFont("Arial", 20)

    # ---------------------------------------------------------
    # TRACK VISIBILITY / SOLO / MUTE
    # ---------------------------------------------------------
    def _rebuild_track_visibility(self):
        for i in range(16):
            tid = i + 1
            try:
                if hasattr(self.track_system, "track_manager") and hasattr(
                    self.track_system.track_manager, "is_effectively_active"
                ):
                    audible = self.track_system.track_manager.is_effectively_active(tid)
                else:
                    audible = True
            except Exception:
                audible = True
            self.track_visibility[i] = audible

        try:
            self.renderer.set_track_visibility(self.track_visibility)
        except Exception:
            pass

    def _on_track_toggle(self, track_id, state):
        self.track_visibility[track_id] = state
        try:
            self.renderer.set_track_visibility(self.track_visibility)
        except Exception:
            pass

    def _on_track_selected(self, track_id):
        self.active_track_id = track_id
        try:
            self.track_system.track_manager.handle_track_selected(track_id + 1)
        except Exception as e:
            print(f"❌ TrackManager active track update error: {e}")

    def _on_track_mute(self, track_id, state):
        try:
            self.track_system.track_manager.set_mute(track_id + 1, state)
        except Exception as e:
            print(f"❌ TrackManager mute update error: {e}")
        self._rebuild_track_visibility()

    def _on_track_solo(self, track_id, state):
        try:
            self.track_system.track_manager.set_solo(track_id + 1, state)
        except Exception as e:
            print(f"❌ TrackManager solo update error: {e}")
        self._rebuild_track_visibility()

    # ---------------------------------------------------------
    # LAYOUT / CANVAS
    # ---------------------------------------------------------
    def build_layout(self, parent):
        self.canvas_ui = CanvasUI(parent)
        self.canvas = self.canvas_ui.get_canvas()

        if hasattr(self.canvas_ui, "set_quantization"):
            self.canvas_ui.set_quantization(self.quantize_division)
        if hasattr(self.canvas_ui, "set_swing"):
            self.canvas_ui.set_swing(self.swing_amount)

    def _apply_quantization_to_canvas(self):
        if self.canvas_ui is None:
            return
        if hasattr(self.canvas_ui, "set_quantization"):
            self.canvas_ui.set_quantization(self.quantize_division)
        if hasattr(self.canvas_ui, "set_swing"):
            self.canvas_ui.set_swing(self.swing_amount)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        # Transport
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

            elif action == "rewind":
                self.current_time_ms = 0
                self.play_start_time = pygame.time.get_ticks()
                self.transport.set_time("00:00.0")

        # Export + Track switcher
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.export_button_rect.collidepoint(event.pos):
                if self.canvas is not None:
                    export_to_png(self.canvas, "export.png")
                    print("[EXPORT] export.png uložený")

            try:
                result = self.track_switcher.handle_event(event)
                if isinstance(result, dict) and "selected_track" in result:
                    self.active_track_id = result["selected_track"]
            except Exception as e:
                print(f"❌ TrackSwitcherUI error: {e}")

        # Quantization shortcuts
        if event.type == pygame.KEYDOWN:
            updated = False

            if event.key == pygame.K_1:
                self.quantize_division = 1.0
                updated = True
            elif event.key == pygame.K_2:
                self.quantize_division = 0.5
                updated = True
            elif event.key == pygame.K_3:
                self.quantize_division = 0.25
                updated = True
            elif event.key == pygame.K_4:
                self.quantize_division = 0.125
                updated = True

            if event.key == pygame.K_q:
                self.swing_amount = 0.0
                updated = True
            elif event.key == pygame.K_w:
                self.swing_amount = 0.3
                updated = True

            if updated:
                self._apply_quantization_to_canvas()

    # ---------------------------------------------------------
    # NOTE EVENTS
    # ---------------------------------------------------------
    def on_note_on(self, event):
        if not isinstance(event, dict):
            return

        track_id = event.get("track_id", 0)
        note = event.get("note")
        if note is None:
            return

        if not self.track_visibility.get(track_id, True):
            return

        velocity = event.get("velocity", 100)

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

        if not self.track_visibility.get(track_id, True):
            return

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

    # ---------------------------------------------------------
    # TIME / BPM
    # ---------------------------------------------------------
    def _update_time(self):
        if self.is_playing:
            self.current_time_ms = pygame.time.get_ticks() - self.play_start_time

            total_ms = self.current_time_ms
            seconds = (total_ms // 1000) % 60
            minutes = (total_ms // 60000)
            tenths = (total_ms % 1000) // 100

            time_str = f"{minutes:02}:{seconds:02}.{tenths}"
            self.transport.set_time(time_str)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        self._update_time()

        # TRANSPORT
        try:
            x, y = self.layout["transport"]
            self.transport.draw(surface.subsurface((x, y, self.width, 50)))
        except Exception:
            pass

        # TRACK SWITCHER
        try:
            x, y = self.layout["track_switcher"]
            self.track_switcher.draw(
                surface.subsurface((x, y, self.width, 60)),
                active_track=self.active_track_id
            )
        except Exception:
            pass

        # PIANO
        try:
            x, y = self.layout["piano"]
            self.piano.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception:
            pass

        # PIANO ROLL
        try:
            x, y = self.layout["piano_roll"]
            self.piano_roll.draw(surface.subsurface((x, y, self.width, 180)))
        except Exception:
            pass

        # STAFF
        try:
            x, y = self.layout["staff"]
            self.staff.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass

        # VISUALIZER
        try:
            x, y = self.layout["visualizer"]
            timestamp = pygame.time.get_ticks() / 1000.0
            self.visualizer.update_bpm_pulse(self.transport.bpm, timestamp)
            self.visualizer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass

        # RENDERER
        try:
            x, y = self.layout["renderer"]
            self.renderer.draw(surface.subsurface((x, y, self.width, 200)))
        except Exception:
            pass

        # EXPORT BUTTON
        pygame.draw.rect(surface, (40, 40, 40), self.export_button_rect)
        text = self.export_font.render("EXPORT", True, (255, 255, 255))
        surface.blit(text, (self.width - 110, 17))
