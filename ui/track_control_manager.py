from .track_visibility_controller import TrackVisibilityController
from .track_selection_controller import TrackSelectionController
from .track_color_map import TrackColorMap


class TrackControlManager:
    """
    Centrálna trieda pre správu všetkých track-related kontrolérov.
    UI používa tento manager ako jednotné API.
    Renderer si z neho číta stav.
    """

    def __init__(self, track_count: int = 16):
        self.track_count = track_count

        # Tri základné controllery Fázy 4
        self.visibility = TrackVisibilityController(track_count)
        self.selection = TrackSelectionController(track_count)
        self.colors = TrackColorMap()

        # Event hooky
        self._listeners = {
            "track_selected": [],
            "visibility_changed": [],
            "color_changed": [],
        }

    # ---------------------------------------------------------
    # EVENT REGISTRÁCIA
    # ---------------------------------------------------------
    def on(self, event_name: str, callback):
        if event_name in self._listeners:
            self._listeners[event_name].append(callback)

    def _emit(self, event_name: str, data):
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(data)
                except Exception:
                    pass

    # ---------------------------------------------------------
    # INTERNÉ POMOCNÉ FUNKCIE
    # ---------------------------------------------------------
    def _clamp_track(self, track: int) -> int:
        """Zabezpečí, že index stopy je v rozsahu 0–track_count-1."""
        try:
            t = int(track)
        except Exception:
            return 0
        return max(0, min(self.track_count - 1, t))

    # ---------------------------------------------------------
    # API pre UI (Track Switcher / Inspector / Selector)
    # ---------------------------------------------------------
    def select_track(self, track: int):
        """Nastaví aktívnu stopu a notifikuje UI."""
        t = self._clamp_track(track)
        self.selection.select(t)
        self._emit("track_selected", {"track": t})

    def set_active_track(self, track: int):
        """Alias pre select_track – UIManager používa túto metódu."""
        self.select_track(track)

    def toggle_visibility(self, track: int):
        """Prepne viditeľnosť danej stopy a notifikuje UI."""
        t = self._clamp_track(track)
        self.visibility.toggle(t)
        self._emit("visibility_changed", {
            "track": t,
            "visible": self.visibility.is_visible(t)
        })

    def set_color(self, track: int, color_hex: str):
        """Nastaví farbu stopy a notifikuje UI."""
        t = self._clamp_track(track)

        # TrackColorMap nemá set_color → bezpečný fallback
        if hasattr(self.colors, "set_color"):
            try:
                self.colors.set_color(t, color_hex)
            except Exception:
                pass

        self._emit("color_changed", {
            "track": t,
            "color": color_hex
        })

    # ---------------------------------------------------------
    # API pre Renderer
    # ---------------------------------------------------------
    def is_visible(self, track: int) -> bool:
        t = self._clamp_track(track)
        return self.visibility.is_visible(t)

    def get_active_track(self) -> int:
        return self.selection.get_active_track()

    def get_color(self, track: int) -> str:
        t = self._clamp_track(track)
        return self.colors.get_color(t)
