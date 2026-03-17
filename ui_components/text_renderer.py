# Text Renderer – displays rendered notation in UI or console

from ..core.logger import Logger

class TextRenderer:
    def __init__(self):
        Logger.info("TextRenderer initialized.")

    def display(self, text):
        """
        Displays rendered notation text.
        Can be replaced later with GUI output.
        """
        try:
            if not text:
                return

            print(text)  # temporary console output
            Logger.info(f"Rendered notation: {text}")

        except Exception as e:
            Logger.error(f"TextRenderer error: {e}")

