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
        try:
            self.event_bus = EventBus()
        except Exception as e:
            Logger.error(f"Failed to initialize EventBus: {e}")
            self.event_bus = None

        try:
            self.config = ConfigManager()
        except Exception as e:
            Logger.error(f"Failed to initialize ConfigManager: {e}")
            self.config = None

        # Track system prepojený s EventBusom
        try:
            self.track_system = TrackSystem(event_bus=self.event_bus)
        except Exception as e:
            Logger.error(f"Failed to initialize TrackSystem: {e}")
            self.track_system = None

        # Notation processor prepojený s EventBusom
        try:
            self.notation_processor = NotationProcessor(
                track_system=self.track_system,
                event_bus=self.event_bus
            )
        except Exception as e:
            Logger.error(f"Failed to initialize NotationProcessor: {e}")
            self.notation_processor = None

        # Odbery udalostí
        if self.event_bus:
            try:
                self.event_bus.subscribe(MIDI_EXPORTED, self._on_midi_exported)
                self.event_bus.subscribe(ERROR_OCCURRED, self._on_error)
            except Exception as e:
                Logger.error(f"Failed to subscribe to events: {e}")

        Logger.info("AppController initialized successfully.")

    # ---------------------------------------------------------
    # ŠTART APLIKÁCIE
    # ---------------------------------------------------------
    def start(self):
        """Štart aplikácie."""
        Logger.info("Application started.")

        if self.event_bus:
            try:
                self.event_bus.publish(APP_STARTED)
                self.event_bus.publish(STATUS_MESSAGE, "App is running")
            except Exception as e:
                Logger.error(f"Failed to publish start events: {e}")

    # ---------------------------------------------------------
    # STOP APLIKÁCIE
    # ---------------------------------------------------------
    def stop(self):
        """Bezpečné ukončenie aplikácie."""
        Logger.info("Application stopped.")

        if self.event_bus:
            try:
                self.event_bus.publish(APP_STOPPED)
            except Exception as e:
                Logger.error(f"Failed to publish stop event: {e}")

    # ---------------------------------------------------------
    # EXPORT MIDI
    # ---------------------------------------------------------
    def export_midi(self, filename="export.mid"):
        """
        Export MIDI:
        - pošle event MIDI_EXPORT_REQUEST
        - spustí export cez NotationProcessor
        """
        Logger.info(f"Export MIDI requested: {filename}")

        if self.event_bus:
            try:
                self.event_bus.publish(MIDI_EXPORT_REQUEST, filename)
            except Exception as e:
                Logger.error(f"Failed to publish MIDI_EXPORT_REQUEST: {e}")

        if self.notation_processor:
