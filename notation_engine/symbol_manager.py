# Symbol Manager – maps rhythmic values and notes to notation symbols

from ..core.logger import Logger

class SymbolManager:
    SYMBOLS = {
        "whole": "𝅝",
        "half": "𝅗𝅥",
        "quarter": "𝅘𝅥",
        "eighth": "𝅘𝅥𝅮",
        "sixteenth": "𝅘𝅥𝅯"
    }

    @staticmethod
    def get_symbol(rhythm_value):
        """Return the musical symbol for a given rhythmic value."""
        try:
            symbol = SymbolManager.SYMBOLS.get(rhythm_value)

            if symbol is None:
                Logger.warning(f"Unknown rhythm value: {rhythm_value}")
                return None

            return symbol

        except Exception as e:
            Logger.error(f"SymbolManager error: {e}")
            return None

