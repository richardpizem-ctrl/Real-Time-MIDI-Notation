from ..core.logger import Logger


class TextRenderer:
    def __init__(self, enabled=True, print_enabled=True):
        self.enabled = enabled
        self.print_enabled = print_enabled

        Logger.info("TextRenderer initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self):
        self.enabled = not self.enabled
        Logger.info(f"TextRenderer toggled: {self.enabled}")

    # ---------------------------------------------------------
    # DISPLAY TEXT
    # ---------------------------------------------------------
    def display(self, text):
        if not self.enabled:
            return

        try:
            safe_text = self._safe_format(text)

            if not safe_text:
                return

            if self.print_enabled:
                print(safe_text)

            Logger.info(f"Rendered notation: {safe_text}")

        except Exception as e:
            Logger.error(f"TextRenderer error: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj):
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"
