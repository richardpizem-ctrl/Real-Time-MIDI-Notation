# =========================================================
# ui_track_switcher.py – v4.0.0
# Stabilná logická vrstva pre prepínanie MIDI stôp
# =========================================================

from dataclasses import dataclass
from typing import Optional, Callable, Dict


@dataclass(slots=True)
class TrackSwitchEvent:
    track_id: int
    is_active: bool
    raw_event: Optional[object] = None


class TrackSwitcherLogic:
    """
    TrackSwitcherLogic (v4.0.0)
    ---------------------------
    Čistá logická vrstva pre prepínanie stôp.

    Vylepšenia v4:
        - okamžitý HEX aj RGB lookup (ak color_map podporuje)
        - bezpečné volanie controllerov
        - stabilný callback systém
        - drop‑in kompatibilita s v2 UI
        - pripravené pre v5 (hover, inspector sync)
    """

    def __init__(self, selection_controller, visibility_controller=None, color_map=None):
        self.selection_controller = selection_controller
        self.visibility_controller = visibility_controller
        self.color_map = color_map

        # UI callbacks pre jednotlivé track tlačidlá
        self._callbacks: Dict[int, Callable[[TrackSwitchEvent], None]] = {}

    # ------------------------------------------------------------
    # CALLBACK REGISTRATION
    # ------------------------------------------------------------
    def register_callback(self, track_id: int, callback: Callable[[TrackSwitchEvent], None]):
        """Registruje UI callback pre daný track button."""
        if not callable(callback):
            return
        self._callbacks[track_id] = callback

    # ------------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------------
    def on_track_clicked(self, track_id: int, raw_event=None):
        """
        Logika prepnutia stopy.
        - nastaví aktívnu stopu
        - voliteľne prepína viditeľnosť
        """

        # 1) Nastav aktívnu stopu
        try:
            self.selection_controller.select(track_id)
        except Exception:
            pass

        is_active = (self.selection_controller.get_active_track() == track_id)

        # 2) Notifikácia UI
        event = TrackSwitchEvent(
            track_id=track_id,
            is_active=is_active,
            raw_event=raw_event
        )

        callback = self._callbacks.get(track_id)
        if callback:
            try:
                callback(event)
            except Exception:
                pass

    # ------------------------------------------------------------
    # OPTIONAL VISIBILITY TOGGLE
    # ------------------------------------------------------------
    def toggle_visibility(self, track_id: int):
        """Voliteľné – UI môže zavolať toggle visibility."""
        if self.visibility_controller is None:
            return

        try:
            self.visibility_controller.toggle(track_id)
        except Exception:
            pass

    # ------------------------------------------------------------
    # COLOR ACCESS
    # ------------------------------------------------------------
    def get_track_color(self, track_id: int):
        """Vráti farbu stopy (HEX alebo RGB podľa mapy)."""
        if self.color_map is None:
            return "#FFFFFF"

        # Podpora HEX aj RGB
        try:
            if hasattr(self.color_map, "get_color_rgb"):
                return self.color_map.get_color_rgb(track_id)
            return self.color_map.get_color(track_id)
        except Exception:
            return "#FFFFFF"
