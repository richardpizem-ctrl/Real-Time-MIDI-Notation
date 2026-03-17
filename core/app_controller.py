# Main application controller – orchestrates all core systems

from .logger import Logger
from .event_bus import EventBus
from .config_manager import ConfigManager
from .device_manager import DeviceManager

from ..midi_input.stream_handler import StreamHandler
from ..notation_engine.notation_renderer import NotationRenderer
from ..ui_components.text_renderer import TextRenderer
from ..ui_components.status_bar import StatusBar
from ..ui_components.debug_panel import DebugPanel

from ..real_time_processing.latency_monitor import LatencyMonitor
from ..real_time_processing.performance_tracker import PerformanceTracker
from ..real_time_processing.error_handler import ErrorHandler


class AppController:
    def __init__(self):
        Logger.info("Initializing AppController...")

        # Core systems
        self.event_bus = EventBus()
        self.config = ConfigManager()
        self.device_manager = DeviceManager()

        # UI components
        self.text_renderer = TextRenderer()
        self.status_bar = StatusBar()
        self.debug_panel = DebugPanel()

        # Notation engine
        self.notation_renderer = NotationRenderer()

        # Real-time processing
        self.latency_monitor = LatencyMonitor()
        self.performance_tracker = PerformanceTracker()
        self.error_handler = ErrorHandler()

        # MIDI stream handler
        self.stream_handler = StreamHandler(
            event_bus=self.event_bus,
            notation_renderer=self.notation_renderer,
            text_renderer=self.text_renderer,
            debug_panel=self.debug_panel
        )

        Logger.info("AppController initialized successfully.")

    def start(self):
        """Start the entire application."""
        try:
            Logger.info("Starting application...")

            # Connect MIDI devices
            self.device_manager.connect()

            # Start stream handler
            self.stream_handler.start()

            Logger.info("Application is now running.")

        except Exception as e:
            self.error_handler.handle(e)

    def stop(self):
        """Stop the application safely."""
        try:
            Logger.info("Stopping application...")

            self.stream_handler.stop()
            self.device_manager.disconnect()

            Logger.info("Application stopped.")

        except Exception as e:
            self.error_handler.handle(e)

