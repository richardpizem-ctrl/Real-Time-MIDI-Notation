# =========================================================
# AppController v4.1.0
# Hlavný orchestrátor systému pre Real-Time MIDI Notation
# Pripravené pre Runtime 5.x (KG, Envoy, System Agent)
# + Editing Layer (v4.2.0 preparation)
# =========================================================

from .logger import Logger
from .event_bus import EventBus
from .config_manager import ConfigManager

# Core modules
from .track_manager import TrackSystem
from .notation_processor import NotationProcessor

# ---------------------------------------------------------
# EDITING LAYER (v4.2.0 preparation)
# ---------------------------------------------------------
from .editing.selection import SelectionSet
from .editing.regions import RegionManager
from .editing.snapping import SnapGrid
from .editing.ghosts import GhostController
from .editing.events import (
    SelectionChangedEvent,
    RegionCreatedEvent,
    RegionSplitEvent,
    GhostNotePreviewEvent,
    GhostRegionPreviewEvent,
)

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
    - inicializáciu všetkých core modulov
    - bezpečné spúšťanie a ukončovanie aplikácie
    - publikovanie systémových udalostí
    - spracovanie exportov a chýb
    - prípravu na Runtime 5.x (KG, Envoy, System Agent)
    - prípravu EDITING layer (v4.2.0)
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        config: ConfigManager | None = None,
        track_system: TrackSystem | None = None,
        notation_processor: NotationProcessor | None = None,
    ):
        Logger.info("Initializing AppController (v4.1.0)...")

        self.is_running = False
        self.version = "4.1.0"

        # -----------------------------------------------------
        # INITIALIZATION OF CORE SYSTEMS
        # -----------------------------------------------------
        self.event_bus = event_bus or self._safe_init(EventBus, "EventBus")
        self.config = config or self._safe_init(ConfigManager, "ConfigManager")

        self.track_system = track_system or self._safe_init(
            lambda: TrackSystem(event_bus=self.event_bus),
            "TrackSystem"
        )

        self.notation_processor = notation_processor or self._safe_init(
            lambda: NotationProcessor(
                track_system=self.track_system,
                event_bus=self.event_bus
            ),
            "NotationProcessor"
        )

        # -----------------------------------------------------
        # INITIALIZATION OF EDITING LAYER (v4.2.0 preparation)
        # -----------------------------------------------------
        self.selection = SelectionSet()
        self.regions = RegionManager()
        self.snap_grid = SnapGrid(0.25)  # default 1/4 beat grid
        self.ghosts = GhostController()

        # -----------------------------------------------------
        # EVENT SUBSCRIPTIONS
        # -----------------------------------------------------
        self._subscribe_events()

        Logger.info("AppController initialized successfully (v4.1.0).")

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

            # -------------------------------------------------
            # EDITING EVENTS (v4.2.0 preparation)
            # -------------------------------------------------
            self.event_bus.subscribe(SelectionChangedEvent, lambda e: None)
            self.event_bus.subscribe(RegionCreatedEvent, lambda e: None)
            self.event_bus.subscribe(RegionSplitEvent, lambda e: None)
            self.event_bus.subscribe(GhostNotePreviewEvent, lambda e: None)
            self.event_bus.subscribe(GhostRegionPreviewEvent, lambda e: None)

        except Exception as e:
            Logger.error(f"Failed to subscribe to events: {e}")

    # ---------------------------------------------------------
    # START APPLICATION
    # ---------------------------------------------------------
    def start(self):
        """Štart aplikácie."""
        if self.is_running:
            Logger.info("Application already running.")
            return

        Logger.info("Application started.")
        self.is_running = True

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
        if not self.is_running:
            Logger.info("Application already stopped.")
            return

        Logger.info("Application stopped.")
        self.is_running = False

        if not self.event_bus:
            Logger.error("EventBus missing — cannot publish APP_STOPPED.")
            return

        try:
            self.event_bus.publish(APP_STOPPED)
        except Exception as e:
            Logger.error(f"Failed to publish stop event: {e}")

    # ---------------------------------------------------------
    # SHUTDOWN (v4.1.0)
    # ---------------------------------------------------------
    def shutdown(self):
        """Úplné vypnutie systému."""
        Logger.info("Shutting down system...")
        self.stop()

        # korektné vypnutie modulov, ak majú shutdown()
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
        """Spustí MIDI export cez event aj priamo cez procesor."""
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
