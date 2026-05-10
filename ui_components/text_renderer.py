# =========================================================
# TextRenderer v4.0.0
# Stable, safe and real‑time friendly text renderer
# =========================================================

from typing import Any
from ..core.logger import Logger


class TextRenderer:
    """
    TextRenderer (v4.0.0)
    ---------------------
    Minimal, stable text renderer for debug output,
    status messages and text-based notation.

    Features:
        - real‑time safe
        - no exceptions
        - safe object formatting
        - toggleable output
        - clean English API
        - ready for v5 (AI/TIMELINE hooks)
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self.print_enabled = bool(print_enabled)

        if self.enabled:
            try:
                Logger.info("TextRenderer initialized.")
            except Exception:
                pass

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle renderer state and return new state."""
        self.enabled = not self.enabled
        try:
            Logger.info(f"TextRenderer toggled: {self.enabled}")
        except Exception:
            pass
        return self.enabled

    # ---------------------------------------------------------
    # DISPLAY TEXT
    # ---------------------------------------------------------
    def display(self, text: Any) -> None:
        """Safely display text."""
        if not self.enabled:
            return

        try:
            safe_text = self._safe_format(text)
            if not safe_text or not safe_text.strip():
                return

            if self.print_enabled:
                print(safe_text)

            Logger.info(f"Rendered text: {safe_text}")

        except Exception:
            try:
                Logger.error("TextRenderer display failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Safely convert object to string."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"
