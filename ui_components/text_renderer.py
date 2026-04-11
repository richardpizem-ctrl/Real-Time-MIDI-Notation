from typing import Any
from ..core.logger import Logger


class TextRenderer:
    """
    TextRenderer (Text Renderer)
    ----------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Jednoduché a bezpečné zobrazovanie textových informácií
        - Používa sa na debug text, status správy, notáciu v textovej forme
        - Všetky chyby sú zachytené a zalogované

    Vlastnosti:
        - Real‑time safe (žiadne blokovanie)
        - Bezpečné formátovanie objektov
        - Možnosť zapnúť/vypnúť výstup
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = enabled
        self.print_enabled = print_enabled

        Logger.info("TextRenderer initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> None:
        """Prepína stav textového renderera (toggle text renderer)."""
        self.enabled = not self.enabled
        Logger.info(f"TextRenderer toggled: {self.enabled}")

    # ---------------------------------------------------------
    # DISPLAY TEXT
    # ---------------------------------------------------------
    def display(self, text: Any) -> None:
        """Bezpečne zobrazí text (display text)."""
        if not self.enabled:
            return

        try:
            safe_text = self._safe_format(text)
            if not safe_text:
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
        """Bezpečne konvertuje objekt na string (safe string conversion)."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"
