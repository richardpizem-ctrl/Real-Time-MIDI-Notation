# Notation Renderer – combines notes, rhythm and symbols into final notation output

from ..core.logger import Logger
from .symbol_manager import SymbolManager

class NotationRenderer:
    def __init__(self):
        Logger.info("NotationRenderer initialized.")

    def render(self, analyzed_notes):
        """
        Takes analyzed notes (with rhythm + pitch info)
        and returns a simple text-based notation line.
        """
        try:
            output = []

            for note in analyzed_notes:
                symbol = SymbolManager.get_symbol(note["rhythm"])

                if symbol is None:
                    symbol = "?"  # fallback symbol

                text = f"{note['note']}{note['octave']} {symbol}"
                output.append(text)

            return " | ".join(output)

        except Exception as e:
            Logger.error(f"NotationRenderer error: {e}")
            return ""
