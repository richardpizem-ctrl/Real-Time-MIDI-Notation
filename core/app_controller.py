# =========================================================
# AppController v2.0.0
# Hlavný orchestrátor systému pre Real-Time MIDI Notation
# =========================================================

from .logger import Logger
from .event_bus import EventBus
from .config_manager import ConfigManager

# Core modules
from .track_manager import TrackSystem
from .notation_processor import NotationProcessor

# Event types
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
    Zodpovedá za:
    - inicializáciu všetkých core modulov
    - bezpečné spúšťanie a ukončovanie aplikácie
    - publikovanie systémových udalostí
    - spracovanie exportov a chýb
    """

    def __init__(self):
        Logger.info("Initializing AppController...")

        # -----------------------------------------------------
        # INITIALIZATION OF CORE SYSTEMS
        # -----------------------------------------------------
        self.event_bus = self._safe_init(EventBus, "EventBus")
        self.config = self._safe_init(ConfigManager, "ConfigManager")

        # Track system prepojený s EventBusom
        self.track_system = self._safe_init(
            lambda: TrackSystem(event_bus=self.event_bus),
            "TrackSystem"
        )

        # Notation processor prepojený s EventBusom
        self.notation_processor = self._safe_init(
            lambda: NotationProcessor(
                track_system=self.track_system,
                event_bus=self.event_bus
            ),
            "NotationProcessor"
        )

        # -----------------------------------------------------
        # EVENT SUBSCRIPTIONS
        # -----------------------------------------------------
        self._subscribe_events()

        Logger.info("AppController initialized successfully.")

    # ---------------------------------------------------------
    # SAFE INITIALIZATION WRAPPER
    # ---------------------------------------------------------
    def _safe_init(self, constructor, name):
        """Bezpečne inicializuje modul a zachytí chyby."""
        try:
            instance = constructor()
            Logger.info(f"{name} initialized.")
            return instance
        except Exception as e:
            Logger.error(f"Failed to initialize {name}: {e}")
            return None

    # ---------------------------------------------------------
    # EVENT SUBSCRIPTIONS
    # ---------------------------------------------------------
    def _subscribe_events(self):
        """Bezpečne registruje event handlery."""
        if not self.event_bus:
            Logger.error("EventBus not available — cannot subscribe to events.")
            return

        try:
            self.event_bus.subscribe(MIDI_EXPORTED, self._on_midi_exported)
            self.event_bus.subscribe(ERROR_OCCURRED, self._on_error)
        except Exception as e:
            Logger.error(f"Failed to subscribe to events: {e}")

    # ---------------------------------------------------------
    # START APPLICATION
    # ---------------------------------------------------------
    def start(self):
        """Štart aplikácie."""
        Logger.info("Application started.")

        if not self.event_bus:
            Logger.error("EventBus missing — cannot publish APP_STARTED.")
            return

        try:
            self.event_bus.publish(APP_STARTED)
            self.event_bus.publish(STATUS_MESSAGE, "App is running")
        except Exception as e:
            Logger.error(f"Failed to publish start events: {e}")

    # ---------------------------------------------------------
    # STOP APPLICATION
    # ---------------------------------------------------------
    def stop(self):
        """Bezpečné ukončenie aplikácie."""
        Logger.info("Application stopped.")

        if not self.event_bus:
            Logger.error("EventBus missing — cannot publish APP_STOPPED.")
            return

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
            try:
                self.notation_processor.export_midi(filename)
            except Exception as e:
                Logger.error(f"NotationProcessor export failed: {e}")

    # ---------------------------------------------------------
    # EVENT HANDLERS
    # ---------------------------------------------------------
    def _on_midi_exported(self, filename):
        Logger.info(f"MIDI exported successfully: {filename}")

        if not self.event_bus:
            return

        try:
            self.event_bus.publish(
                STATUS_MESSAGE,
                f"MIDI exported: {filename}"
            )
        except Exception as e:
            Logger.error(f"Failed to publish STATUS_MESSAGE: {e}")

    def _on_error(self, error_message):
        Logger.error(f"Application error: {error_message}")

        if not self.event_bus:
            return

        try:
            self.event_bus.publish(
                STATUS_MESSAGE,
                f"Error: {error_message}"
            )
        except Exception as e:
            Logger.error(f"Failed to publish STATUS_MESSAGE: {e}")
