# =========================================================
# AppController v4.1.0
# Hlavný orchestrátor systému pre Real-Time MIDI Notation
# Pripravené pre Runtime 5.x (KG, Envoy, System Agent)
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
    Centrálny kontrolér aplikácie (v4.1.0).

    Zodpovedá za:
    - inicializáciu core modulov
    - bezpečné spúšťanie a ukončovanie aplikácie
    - publikovanie systémových udalostí
    - spracovanie exportov a chýb
    - prípravu na Runtime 5.x (KG, Envoy, System Agent)
    """

    def __init__(self):
        Logger.info("Initializing AppController (v4.1.0)...")

        self.is_running = False

        # -----------------------------------------------------
        # INITIALIZATION OF CORE SYSTEMS
        # -----------------------------------------------------
        self.event_bus = self._safe_init(EventBus, "EventBus")
        self.config = self._safe_init(ConfigManager, "ConfigManager")

        self.track_system = self._safe_init(
            lambda: TrackSystem(event_bus=self.event_bus),
            "TrackSystem"
        )

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

        Logger.info("AppController initialized successfully (v4.1.0).")

    # ---------------------------------------------------------
    # SAFE INITIALIZATION WRAPPER
    # ---------------------------------------------------------
    def _safe_init(self, constructor, name):
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
        if self.is_running:
            Logger.info("Application already running.")
            return

        Logger.info("Application started.")
        self.is_running = True

        if self.event_bus:
            try:
                self.event_bus.publish(APP_STARTED)
                self.event_bus.publish(STATUS_MESSAGE, "App is running")
            except Exception as e:
                Logger.error(f"Failed to publish start events: {e}")

    # ---------------------------------------------------------
    # STOP APPLICATION
    # ---------------------------------------------------------
    def stop(self):
        if not self.is_running:
            Logger.info("Application already stopped.")
            return

        Logger.info("Application stopped.")
        self.is_running = False

        if self.event_bus:
            try:
                self.event_bus.publish(APP_STOPPED)
            except Exception as e:
                Logger.error(f"Failed to publish stop event: {e}")

    # ---------------------------------------------------------
    # SHUTDOWN (v4.1.0)
    # ---------------------------------------------------------
    def shutdown(self):
        Logger.info("Shutting down system...")
        self.stop()

        for name, module in [
            ("NotationProcessor", self.notation_processor),
            ("TrackSystem", self.track_system),
        ]:
            if hasattr(module, "shutdown") and callable(module.shutdown):
                try:
                    module.shutdown()
                    Logger.info(f"{name} shutdown completed.")
                except Exception as e:
                    Logger.error(f"Failed to shutdown {name}: {e}")

    # ---------------------------------------------------------
    # EXPORT MIDI
    # ---------------------------------------------------------
    def export_midi(self, filename="export.mid"):
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

        if self.event_bus:
            try:
                self.event_bus.publish(
                    STATUS_MESSAGE,
                    f"MIDI exported: {filename}"
                )
            except Exception as e:
                Logger.error(f"Failed to publish STATUS_MESSAGE: {e}")

    def _on_error(self, error_message):
        Logger.error(f"Application error: {error_message}")

        if self.event_bus:
            try:
                self.event_bus.publish(
                    STATUS_MESSAGE,
                    f"Error: {error_message}"
                )
            except Exception as e:
                Logger.error(f"Failed to publish STATUS_MESSAGE: {e}")
