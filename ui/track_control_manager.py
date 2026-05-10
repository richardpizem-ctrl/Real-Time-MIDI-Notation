# =========================================================
# TrackControlManager v4.0.0
# Centrálna správa track visibility, selection a farieb
# =========================================================

from typing import Callable, Dict, Any, List

from .track_visibility_controller import TrackVisibilityController
from .track_selection_controller import TrackSelectionController
from .track_color_map import TrackColorMap


class TrackControlManager:
    """
    TrackControlManager (v4.0.0)
    ----------------------------
    Centrálna trieda pre správu všetkých track-related kontrolérov.

    Používajú ju:
        - UI (Track Switcher, Track Selector, Inspector)
        - Renderer (GraphicNotationRenderer)
        - Timeline (track lanes)
        - MIDI pipeline (routing)

    Funkcie:
        - výber aktívnej stopy
        - prepínanie viditeľnosti
        - poskytovanie farieb (HEX + RGB)
        - event hooky (track_selected, visibility_changed, color_changed)
        - real‑time safe, stabilné, pripravené na v5 (dynamic tracks)
    """

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)

        # Tri základné controllery
        self.visibility = TrackVisibilityController(self.track_count)
        self.selection = TrackSelectionController(self.track_count)
        self.colors = TrackColorMap()

        # Event hooky
        self._listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {
            "track_selected": [],
            "visibility_changed": [],
            "color_changed": [],
        }

    # ---------------------------------------------------------
    # EVENT REGISTRÁCIA
    # ---------------------------------------------------------
    def on(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Registruje callback pre daný event (bezpečný, real‑time safe)."""
        if event_name not in self._listeners:
            return
        if not callable(callback):
            return
        self._listeners[event_name].append(callback)

    def _emit(self, event_name: str, data: Dict[str, Any]) -> None:
        """Bezpečne notifikuje všetkých listenerov."""
        listeners = self._listeners.get(event_name)
        if not listeners:
            return
        for callback in listeners:
            try:
                callback(data)
            except Exception:
                # Event hooky nesmú nikdy zhodiť real‑time pipeline
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
    def select_track(self, track: int) -> None:
        """Nastaví aktívnu stopu a notifikuje UI."""
        t = self._clamp_track(track)
        self.selection.select(t)
        self._emit("track_selected", {"track": t})

    def set_active_track(self, track: int) -> None:
        """Alias pre select_track – UIManager používa túto metódu."""
        self.select_track(track)

    def toggle_visibility(self, track: int) -> None:
        """Prepne viditeľnosť danej stopy a notifikuje UI."""
        t = self._clamp_track(track)
        self.visibility.toggle(t)
        self._emit(
            "visibility_changed",
            {
                "track": t,
                "visible": self.visibility.is_visible(t),
            },
        )

    def set_color(self, track: int, color_hex: str) -> None:
        """
        Nastaví farbu stopy a notifikuje UI.
        TrackColorMap je read‑only → iba emitujeme event.
        """
        t = self._clamp_track(track)
        self._emit(
            "color_changed",
            {
                "track": t,
                "color": color_hex,
            },
        )

    # ---------------------------------------------------------
    # API pre Renderer
    # ---------------------------------------------------------
    def is_visible(self, track: int) -> bool:
        t = self._clamp_track(track)
        return self.visibility.is_visible(t)

    def get_active_track(self) -> int:
        return self.selection.get_active_track()

    def get_color(self, track: int) -> str:
        """Vráti HEX farbu pre danú stopu."""
        t = self._clamp_track(track)
        return self.colors.get_color(t)

    def get_color_rgb(self, track: int):
        """Vráti RGB farbu pre danú stopu (r, g, b)."""
        t = self._clamp_track(track)
        return self.colors.get_color_rgb(t)
