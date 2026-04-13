import pygame
from .piano_ui import PianoUI
from .piano_roll_ui import PianoRollUI
from .staff_ui import StaffUI
from .note_visualizer_ui import NoteVisualizerUI
from .track_switcher_ui import TrackSwitcherUI
from .track_selector_ui import TrackSelectorUI
from .canvas_ui import CanvasUI
from .transport_ui import TransportUI
from .track_inspector import TrackInspector
from .timeline_ui import TimelineUI
from .pixel_layout_engine import PixelLayoutEngine

from .track_control_manager import TrackControlManager
from renderer_new.graphic_renderer import GraphicNotationRenderer
from renderer.exporter import export_to_png


class UIManager:
    def __init__(self, width, height, track_system, notation_processor):
        self.width = width
        self.height = height
        self.track_system = track_system
        self.notation_processor = notation_processor

        pygame.font.init()

        # ---------------------------------------------------------
        # TRACK CONTROL MANAGER
        # ---------------------------------------------------------
        self.track_control = TrackControlManager(track_count=16)
        self.track_control.on("track_selected", self._on_track_selected)
        self.track_control.on("visibility_changed", self._on_visibility_changed)
        self.track_control.on("color_changed", self._on_color_changed)

        # ---------------------------------------------------------
        # TRANSPORT
        # ---------------------------------------------------------
        self.transport = TransportUI(width, 50)
        self.is_playing = False
        self.play_start_time = 0
        self.current_time_ms = 0

        # ---------------------------------------------------------
        # RENDERER (musí byť vytvorený PRED TimelineUI)
        # ---------------------------------------------------------
        self.renderer = GraphicNotationRenderer(
            width,
            200,
            track_system,
            self.track_control,
        )

        # ---------------------------------------------------------
        # TIMELINE (prepojené s renderer.timeline_controller)
        # ---------------------------------------------------------
        self.timeline = TimelineUI(
            x=0,
            y=50,
            width=width,
            height=80,
            event_bus=track_system.event_bus,
            renderer=self.renderer,   # PREPOJENIE
        )

        # ---------------------------------------------------------
        # TRACK SWITCHER
        # ---------------------------------------------------------
        self.track_switcher = TrackSwitcherUI(
            x=0,
            y=130,
            width=width,
            height=60,
            track_colors=None,
            event_bus=track_system.event_bus,
            track_control_manager=self.track_control,
        )

        # ---------------------------------------------------------
        # TRACK SELECTOR
        # ---------------------------------------------------------
        self.track_selector = TrackSelectorUI(
            track_control_manager=self.track_control,
            width=width,
            height=60,
        )

        # ---------------------------------------------------------
        # UI PANELY
        # ---------------------------------------------------------
        self.piano = PianoUI(width, 180)
        self.piano_roll = PianoRollUI(width, 180)
        self.staff = StaffUI(width, 200)
        self.visualizer = NoteVisualizerUI(width, 200)

        # ---------------------------------------------------------
        # TRACK INSPECTOR
        # ---------------------------------------------------------
        self.track_inspector = TrackInspector(
            track_manager=self.track_system,
            track_control=self.track_control,
            x=0,
            y=1180,
            width=260,
            height=400,
        )

        # Canvas (Tk)
        self.canvas_ui = None
        self.canvas = None

        # Quantization
        self.quantize_division = 1.0
        self.swing_amount = 0.0

        # ---------------------------------------------------------
        # PIXEL LAYOUT ENGINE (FÁZA 5)
        # ---------------------------------------------------------
        self.layout_engine = PixelLayoutEngine()

        # Layout dict (Rect objekty)
        self.layout = {}

        self.export_button_rect = pygame.Rect(self.width - 120, 10, 110, 35)
        self.export_font = pygame.font.SysFont("Arial", 20)

    # ---------------------------------------------------------
    # CANVAS
    # ---------------------------------------------------------
    def build_layout(self, parent):
        self.canvas_ui = CanvasUI(parent)
        self.canvas = self.canvas_ui.get_canvas()

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

        # Timeline
        try:
            self.timeline.handle_event(event)
        except:
            pass

        # Export + Track switcher + Track selector + Track inspector
        if event.type == pygame.MOUSEBUTTONDOWN:

            # EXPORT
            if self.export_button_rect.collidepoint(event.pos):
                if self.canvas is not None:
                    export_to_png(self.canvas, "export.png")
                    print("[EXPORT] export.png uložený")

            # Track Switcher
            try:
                result = self.track_switcher.handle_event(event)
                if isinstance(result, dict) and "selected_track" in result:
                    self.track_control.set_active_track(result["selected_track"])
            except:
                pass

            # Track Selector
            try:
                self.track_selector.handle_click(event.pos)
            except:
                pass

            # Track Inspector
            try:
                self.track_inspector.handle_event(event)
            except:
                pass

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
    # TIME UPDATE
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

            try:
                self.renderer.set_playback_time(total_ms / 1000.0)
            except:
                pass

    # ---------------------------------------------------------
    # TRACK CONTROL CALLBACKS
    # ---------------------------------------------------------
    def _on_track_selected(self, data):
        track = data.get("track", 0)
        try:
            self.track_selector.set_active_track(track)
        except:
            pass
        try:
            self.track_switcher.set_active_track(track)
        except:
            pass
        try:
            self.track_inspector.set_active_track(track)
        except:
            pass

    def _on_visibility_changed(self, data):
        track = data.get("track", 0)
        visible = data.get("visible", True)
        try:
            self.track_switcher.update_visibility(track, visible)
        except:
            pass
        try:
            self.renderer.update_visibility(track, visible)
        except:
            pass

    def _on_color_changed(self, data):
        track = data.get("track", 0)
        color = data.get("color", "#FFFFFF")
        try:
            self.track_switcher.update_color(track, color)
        except:
            pass
        try:
            self.renderer.update_color(track, color)
        except:
            pass
        try:
            self.track_inspector.update_color(track, color)
        except:
            pass

    # ---------------------------------------------------------
    # QUANTIZATION → CANVAS
    # ---------------------------------------------------------
    def _apply_quantization_to_canvas(self):
        if self.canvas_ui is None:
            return
        try:
            if hasattr(self.canvas_ui, "set_quantization"):
                self.canvas_ui.set_quantization(self.quantize_division)
            if hasattr(self.canvas_ui, "set_swing"):
                self.canvas_ui.set_swing(self.swing_amount)
        except:
            pass

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        self._update_time()

        # Prepočítať layout
        self.layout = self.layout_engine.compute_layout(self.width, self.height)

        # TRANSPORT
        try:
            r = self.layout["transport"]
            self.transport.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # TIMELINE
        try:
            r = self.layout["timeline"]
            self.timeline.set_bounds(r.x, r.y, r.w, r.h)
            self.timeline.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # TRACK SWITCHER
        try:
            r = self.layout["track_switcher"]
            self.track_switcher.draw(
                surface.subsurface((r.x, r.y, r.w, r.h)),
                active_track=self.track_control.get_active_track(),
            )
        except:
            pass

        # TRACK SELECTOR
        try:
            r = self.layout["track_selector"]
            self.track_selector.draw(
                surface.subsurface((r.x, r.y, r.w, r.h)),
                active_track=self.track_control.get_active_track(),
            )
        except:
            pass

        # PIANO
        try:
            r = self.layout["piano"]
            self.piano.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # PIANO ROLL
        try:
            r = self.layout["piano_roll"]
            self.piano_roll.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # STAFF
        try:
            r = self.layout["staff"]
            self.staff.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # VISUALIZER
        try:
            r = self.layout["visualizer"]
            timestamp = pygame.time.get_ticks() / 1000.0
            self.visualizer.update_bpm_pulse(self.transport.bpm, timestamp)
            self.visualizer.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # RENDERER
        try:
            r = self.layout["renderer"]
            self.renderer.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # TRACK INSPECTOR
        try:
            r = self.layout["track_inspector"]
            self.track_inspector.draw(surface.subsurface((r.x, r.y, r.w, r.h)))
        except:
            pass

        # ---------------------------------------------------------
        # FAREBNÁ LEGENDA (ŽLTÁ / ZELENÁ / ČERVENÁ / MODRÁ)
        # ---------------------------------------------------------
        legend_x = 20
        legend_y = self.height - 160
        legend_font = pygame.font.SysFont("Arial", 18)

        try:
            pygame.draw.rect(surface, (25, 25, 25), (legend_x - 10, legend_y - 10, 260, 150))

            title = legend_font.render("Dynamika / Chyby", True, (255, 255, 255))
            surface.blit(title, (legend_x, legend_y))

            pygame.draw.rect(surface, (255, 220, 0), (legend_x, legend_y + 30, 20, 20))
            surface.blit(
                legend_font.render("Slabá (1–50)", True, (255, 255, 255)),
                (legend_x + 30, legend_y + 30),
            )

            pygame.draw.rect(surface, (0, 200, 0), (legend_x, legend_y + 60, 20, 20))
            surface.blit(
                legend_font.render("Stredná (51–90)", True, (255, 255, 255)),
                (legend_x + 30, legend_y + 60),
            )

            pygame.draw.rect(surface, (255, 60, 60), (legend_x, legend_y + 90, 20, 20))
            surface.blit(
                legend_font.render("Silná (91–127)", True, (255, 255, 255)),
                (legend_x + 30, legend_y + 90),
            )

            pygame.draw.rect(surface, (0, 120, 255), (legend_x, legend_y + 120, 20, 20))
            surface.blit(
                legend_font.render("Chyba (error)", True, (255, 255, 255)),
                (legend_x + 30, legend_y + 120),
            )
        except:
            pass

        # ---------------------------------------------------------
        # EXPORT BUTTON
        # ---------------------------------------------------------
        pygame.draw.rect(surface, (40, 40, 40), self.export_button_rect)
        text = self.export_font.render("EXPORT", True, (255, 255, 255))
        surface.blit(text, (self.width - 110, 17))
