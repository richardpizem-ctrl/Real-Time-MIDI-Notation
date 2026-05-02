# =========================================================
# DebugPanel v2.0.0
# Stabilné, bezpečné a real‑time friendly debug logovanie
# =========================================================

import pygame
from typing import Any
from ..core.logger import Logger


class DebugPanel:
    """
    DebugPanel (v2.0.0)
    -------------------
    Bezpečné logovanie udalostí, pipeline krokov a chýb.

    Vlastnosti:
        - žiadne výnimky nesmú preraziť do UI
        - real‑time safe
        - jednotné API
        - bezpečné formátovanie objektov
        - toggle debug módu
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self.print_enabled = bool(print_enabled)

        if self.enabled:
            Logger.info("DebugPanel initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Prepína stav debug panelu a vráti nový stav."""
        self.enabled = not self.enabled
        Logger.info(f"DebugPanel toggled: {self.enabled}")
        return self.enabled

    # ---------------------------------------------------------
    # MIDI EVENT LOGGING
    # ---------------------------------------------------------
    def log_midi_event(self, event: Any) -> None:
        """Loguje MIDI udalosť."""
        if not self.enabled:
            return

        try:
            safe_event = self._safe_format(event)

            if self.print_enabled:
                print(f"[MIDI EVENT] {safe_event}")

            Logger.info(f"Debug MIDI event: {safe_event}")

        except Exception as e:
            Logger.error(f"DebugPanel MIDI error: {e}")

    # ---------------------------------------------------------
    # PIPELINE LOGGING
    # ---------------------------------------------------------
    def log_pipeline(self, stage: str, data: Any) -> None:
        """Loguje pipeline krok."""
        if not self.enabled:
            return

        try:
            safe_data = self._safe_format(data)

            if self.print_enabled:
                print(f"[PIPELINE] {stage}: {safe_data}")

            Logger.info(f"Debug pipeline {stage}: {safe_data}")

        except Exception as e:
            Logger.error(f"DebugPanel pipeline error: {e}")

    # ---------------------------------------------------------
    # ERROR LOGGING
    # ---------------------------------------------------------
    def log_error(self, message: Any) -> None:
        """Loguje chybu."""
        try:
            safe_msg = self._safe_format(message)

            if self.print_enabled:
                print(f"[ERROR] {safe_msg}")

            Logger.error(f"DebugPanel error: {safe_msg}")

        except Exception as e:
            Logger.error(f"DebugPanel logging failure: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Bezpečne konvertuje objekt na string."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable object>"
