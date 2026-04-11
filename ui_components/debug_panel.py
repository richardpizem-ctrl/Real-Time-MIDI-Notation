import pygame
from typing import Any
from ..core.logger import Logger


class DebugPanel:
    """
    DebugPanel (Debug Panel)
    ------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Bezpečné logovanie MIDI udalostí (MIDI events)
        - Logovanie pipeline krokov (pipeline stages)
        - Jednotné error logovanie
        - Možnosť zapnúť/vypnúť debug mód
        - Bezpečné formátovanie objektov

    Vlastnosti:
        - Žiadne výnimky nesmú preraziť do UI
        - Všetky chyby sú zachytené a zalogované
        - Kompatibilné s real‑time slučkou
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = enabled
        self.print_enabled = print_enabled
        Logger.info("DebugPanel initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> None:
        """Prepína stav debug panelu (toggle debug panel)."""
        self.enabled = not self.enabled
        Logger.info(f"DebugPanel toggled: {self.enabled}")

    # ---------------------------------------------------------
    # MIDI EVENT LOGGING
    # ---------------------------------------------------------
    def log_midi_event(self, event: Any) -> None:
        """Loguje MIDI udalosť (MIDI event)."""
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
        """Loguje pipeline krok (pipeline stage)."""
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
    def log_error(self, message: str) -> None:
        """Loguje chybu (error)."""
        try:
            if self.print_enabled:
                print(f"[ERROR] {message}")

            Logger.error(f"DebugPanel error: {message}")

        except Exception as e:
            Logger.error(f"DebugPanel logging failure: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Bezpečne konvertuje objekt na string (safe string conversion)."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable object>"
