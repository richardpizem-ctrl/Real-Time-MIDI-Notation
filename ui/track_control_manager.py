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

    # -----------------------------
    # API pre UI (Track Switcher)
    # -----------------------------

    def select_track(self, track: int):
        """Nastaví aktívnu stopu."""
        self.selection.select(track)

    def toggle_visibility(self, track: int):
        """Prepne viditeľnosť danej stopy."""
        self.visibility.toggle(track)

    # -----------------------------
    # API pre Renderer
    # -----------------------------

    def is_visible(self, track: int) -> bool:
        """Vráti, či je stopa viditeľná."""
        return self.visibility.is_visible(track)

    def get_active_track(self) -> int:
        """Vráti index aktívnej stopy."""
        return self.selection.get_active_track()

    def get_color(self, track: int) -> str:
        """Vráti farbu danej stopy."""
        return self.colors.get_color(track)
