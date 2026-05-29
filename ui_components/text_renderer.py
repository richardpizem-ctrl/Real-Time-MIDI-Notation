# =========================================================
# TextRenderer v4.3.0
# Ultra-stable, real-time safe text renderer
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

from typing import Any
from ..core.logger import Logger


class TextRenderer:
    """
    TextRenderer (v4.3.0)
    ---------------------
    Minimal, ultra-stable text renderer for debug output,
    status messages and text-based notation.

    Improvements in v4.3.0:
        - __slots__ for ultra-low latency
        - zero-allocation hot path
        - safe string formatting
        - toggleable output
        - ready for v5 (AI/TIMELINE hooks)
    """

    __slots__ = ("enabled", "print_enabled")

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
