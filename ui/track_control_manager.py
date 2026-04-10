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

        # ---------------------------------------------------------
        # EVENT HOOKS (NOVÉ)
        # ---------------------------------------------------------
        # Každý listener je funkcia, ktorú UI alebo renderer zaregistruje.
        self._listeners = {
            "track_selected": [],
            "visibility_changed": [],
            "color_changed": [],
        }

    # ---------------------------------------------------------
    # EVENT REGISTRÁCIA
    # ---------------------------------------------------------
    def on(self, event_name: str, callback):
        """UI alebo renderer môže zaregistrovať callback."""
        if event_name in self._listeners:
            self._listeners[event_name].append(callback)

    def _emit(self, event_name: str, data):
        """Interné volanie eventov."""
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(data)
                except Exception:
                    pass
    # ---------------------------------------------------------
    # API pre UI (Track Switcher / Inspector / Selector)
    # ---------------------------------------------------------

    def select_track(self, track: int):
        """Nastaví aktívnu stopu a notifikuje UI."""
        self.selection.select(track)
        self._emit("track_selected", {"track": track})

    def toggle_visibility(self, track: int):
        """Prepne viditeľnosť danej stopy a notifikuje UI."""
        self.visibility.toggle(track)
        self._emit("visibility_changed", {
            "track": track,
            "visible": self.visibility.is_visible(track)
        })

    def set_color(self, track: int, color_hex: str):
        """Nastaví farbu stopy a notifikuje UI."""
        self.colors.set_color(track, color_hex)
        self._emit("color_changed", {
            "track": track,
            "color": color_hex
        })

    # ---------------------------------------------------------
    # API pre Renderer
    # ---------------------------------------------------------

    def is_visible(self, track: int) -> bool:
        """Vráti, či je stopa viditeľná."""
        return self.visibility.is_visible(track)

    def get_active_track(self) -> int:
        """Vráti index aktívnej stopy."""
        return self.selection.get_active_track()

    def get_color(self, track: int) -> str:
        """Vráti farbu danej stopy."""
        return self.colors.get_color(track)
