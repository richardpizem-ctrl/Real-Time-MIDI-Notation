# Main application controller – orchestrates all core systems

from .logger import Logger
from .event_bus import EventBus
from .config_manager import ConfigManager

# Nové importy – naše reálne funkčné moduly
from .track_manager import TrackSystem
from .notation_processor import NotationProcessor


class AppController:
    """
    Minimalistický, funkčný AppController pre tvoj projekt.
    Obsahuje:
    - TrackSystem
    - NotationProcessor
    - EventBus
    - ConfigManager
    """

    def __init__(self):
        Logger.info("Initializing AppController...")

        # Core systems
        self.event_bus = EventBus()
        self.config = ConfigManager()

        # Track system
        self.track_system = TrackSystem()

        # Notation processor (export MIDI)
        self.notation_processor = NotationProcessor(self.track_system)

        Logger.info("AppController initialized successfully.")

    def start(self):
        """
        Štart aplikácie – v tejto minimalistickej verzii
        nemusíme pripájať zariadenia ani spúšťať streamy.
        """
        Logger.info("Application started.")

    def stop(self):
        """Bezpečné ukončenie aplikácie."""
        Logger.info("Application stopped.")

    def export_midi(self, filename="export.mid"):
        """Export MIDI cez NotationProcessor."""
        try:
            self.notation_processor.export_to_midi(filename)
            Logger.info(f"MIDI export completed: {filename}")
        except Exception as e:
            Logger.error(f"MIDI export failed: {e}")
