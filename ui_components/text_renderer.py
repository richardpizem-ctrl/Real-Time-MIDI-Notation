# =========================================================
# TextRenderer v2.0.0
# Stabilné, bezpečné a real‑time friendly textové logovanie
# =========================================================

from typing import Any
from ..core.logger import Logger


class TextRenderer:
    """
    TextRenderer (v2.0.0)
    ---------------------
    Jednoduchý, stabilný textový renderer pre debug, status
    a textovú notáciu.

    Vlastnosti:
        - real‑time safe
        - žiadne výnimky nesmú preraziť do UI
        - bezpečné formátovanie objektov
        - toggle výstupu
        - pripravené pre v3 (AI/TIMELINE hooks)
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self.print_enabled = bool(print_enabled)

        if self.enabled:
            Logger.info("TextRenderer initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Prepína stav textového renderera a vráti nový stav."""
        self.enabled = not self.enabled
        Logger.info(f"TextRenderer toggled: {self.enabled}")
        return self.enabled

    # ---------------------------------------------------------
    # DISPLAY TEXT
    # ---------------------------------------------------------
    def display(self, text: Any) -> None:
        """Bezpečne zobrazí text."""
        if not self.enabled:
            return

        try:
            safe_text = self._safe_format(text)
            if not safe_text or safe_text.strip() == "":
                return

            if self.print_enabled:
                print(safe_text)

            Logger.info(f"Rendered text: {safe_text}")

        except Exception as e:
            Logger.error(f"TextRenderer error: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Bezpečne konvertuje objekt na string."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"
