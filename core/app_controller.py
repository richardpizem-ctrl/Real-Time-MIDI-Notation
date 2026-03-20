# Main application controller – orchestrates all core systems

from .logger import Logger
from .event_bus import EventBus
from .config_manager import ConfigManager

# Reálne funkčné moduly
from .track_manager import TrackSystem
from .notation_processor import NotationProcessor

# Event typy
from .event_types import (
    APP_STARTED,
    APP_STOPPED,
    STATUS_MESSAGE,
    MIDI_EXPORT_REQUEST,
    MIDI_EXPORTED,
    ERROR_OCCURRED,
)


class AppController:
    """
    Centrálny kontrolér aplikácie.
    Riadi:
    - EventBus
    - TrackSystem
    - NotationProcessor
    - systémové udalosti
    """

    def __init__(self):
        Logger.info("Initializing AppController...")

        # Core systems
        self.event_bus = EventBus()
        self.config = ConfigManager()

        # Track system prepojený s EventBusom
        self.track_system = TrackSystem(event_bus=self.event_bus)

        # Notation processor prepojený s EventBusom
        self.notation_processor = NotationProcessor(
            track_system=self.track_system,
            event_bus=self.event_bus
        )

        # Odbery udalostí
        self.event_bus.subscribe(MIDI_EXPORTED, self._on_midi_exported)
        self.event_bus.subscribe(ERROR_OCCURRED, self._on_error)

        Logger.info("AppController initialized successfully.")

    def start(self):
        """Štart aplikácie."""
        Logger.info("Application started.")
        self.event_bus.publish(APP_STARTED)
        self.event_bus.publish(STATUS_MESSAGE, "App is running")

    def stop(self):
        """Bezpečné ukončenie aplikácie."""
        Logger.info("Application stopped.")
        self.event_bus.publish(APP_STOPPED)

    def export_midi(self, filename="export.mid"):
        """
        Export MIDI:
        - pošle event MIDI_EXPORT_REQUEST
        - spustí export cez NotationProcessor
        """
        Logger.info(f"Export MIDI requested: {filename}")
        self.event_bus.publish(MIDI_EXPORT_REQUEST, filename)
        self.notation_processor.export_to_midi(filename)

    # ===== Handlery udalostí =====

    def _on_midi_exported(self, filename: str):
        Logger.info(f"MIDI export completed (event): {filename}")
        self.event_bus.publish(STATUS_MESSAGE, f"MIDI exported: {filename}")

    def _on_error(self, message: str):
        Logger.error(f"Error event received: {message}")
