# =========================================================
# AppController v4-ready
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
    Centrálny kontrolér aplikácie (v4-ready).
    Pripravený na:
    - AI engine
    - Real-time engine
    - rozšíriteľnú architektúru
    """

    def __init__(self):
        Logger.info("Initializing AppController (v4-ready)...")

        self.is_running = False
        self.ai_engine = None
        self.realtime_engine = None

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

        Logger.info("AppController initialized successfully (v4-ready).")

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
    # AI / REAL-TIME HOOKS (v4-ready)
    # ---------------------------------------------------------
    def register_ai_engine(self, ai_engine):
        self.ai_engine = ai_engine
        Logger.info("AI engine registered.")

    def register_realtime_engine(self, realtime_engine):
        self.realtime_engine = realtime_engine
        Logger.info("Real-time engine registered.")

    def start_realtime(self):
        if self.realtime_engine:
            try:
                self.realtime_engine.start()
                Logger.info("Real-time engine started.")
            except Exception as e:
                Logger.error(f"Failed to start real-time engine: {e}")

    def stop_realtime(self):
        if self.realtime_engine:
            try:
                self.realtime_engine.stop()
                Logger.info("Real-time engine stopped.")
            except Exception as e:
                Logger.error(f"Failed to stop real-time engine: {e}")

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

        # v4-ready: automatické spustenie real-time engine
        self.start_realtime()

    # ---------------------------------------------------------
    # STOP APPLICATION
    # ---------------------------------------------------------
    def stop(self):
        if not self.is_running:
            Logger.info("Application already stopped.")
            return

        Logger.info("Application stopped.")
        self.is_running = False

        # v4-ready: najprv zastaviť real-time engine
        self.stop_realtime()

        if self.event_bus:
            try:
                self.event_bus.publish(APP_STOPPED)
            except Exception as e:
                Logger.error(f"Failed to publish stop event: {e}")

    # ---------------------------------------------------------
    # SHUTDOWN (v4-ready)
    # ---------------------------------------------------------
    def shutdown(self):
        Logger.info("Shutting down system...")
        self.stop()

        # v4-ready: korektné vypnutie modulov
        for name, module in [
            ("AI engine", self.ai_engine),
            ("Real-time engine", self.realtime_engine),
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

        # v4-ready: AI post-export hook
        if self.ai_engine and hasattr(self.ai_engine, "on_midi_exported"):
            try:
                self.ai_engine.on_midi_exported(filename)
            except Exception as e:
                Logger.error(f"AI engine post-export hook failed: {e}")

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
