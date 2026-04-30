# DeviceManager – Fáza 4 verzia pre Real-Time-MIDI-Notation
import threading
import mido
from core.logger import Logger
from core.event_types import ERROR_OCCURRED
from core.event_bus import EventBus


class DeviceManager:
    """
    Stabilný MIDI Device Manager (Fáza 4):
    - bezpečné zisťovanie MIDI zariadení
    - thread-safe refresh
    - bezpečné otváranie / zatváranie portov
    - Logger namiesto print()
    - EventBus integrácia (voliteľná)
    """

    def __init__(self, event_bus: EventBus | None = None):
        self.event_bus = event_bus

        self.available_inputs: list[str] = []
        self.selected_input: str | None = None
        self.input_port = None

        self._lock = threading.Lock()

        self.refresh_devices()

    # ---------------------------------------------------------
    # REFRESH DEVICE LIST
    # ---------------------------------------------------------
    def refresh_devices(self) -> None:
        """Aktualizuje zoznam dostupných MIDI vstupov (thread-safe)."""
        with self._lock:
            try:
                self.available_inputs = list(mido.get_input_names())
                Logger.info(f"DeviceManager: Found {len(self.available_inputs)} MIDI inputs.")
            except Exception as e:
                Logger.error(f"DeviceManager: Failed to refresh devices: {e}")
                self.available_inputs = []
                self._publish_error(f"MIDI device scan failed: {e}")

    # ---------------------------------------------------------
    # LIST DEVICES
    # ---------------------------------------------------------
    def list_devices(self) -> list[str]:
        """Vráti zoznam dostupných MIDI vstupov."""
        with self._lock:
            return list(self.available_inputs)

    # ---------------------------------------------------------
    # SELECT DEVICE
    # ---------------------------------------------------------
    def select_device(self, index: int) -> bool:
        """Vyberie MIDI zariadenie podľa indexu."""
        with self._lock:
            if not self.available_inputs:
                Logger.warning("DeviceManager: No MIDI devices found.")
                return False

            if not isinstance(index, int) or index < 0 or index >= len(self.available_inputs):
                Logger.warning(f"DeviceManager: Invalid device index {index}.")
                return False

            self.selected_input = self.available_inputs[index]
            Logger.info(f"DeviceManager: Selected device → {self.selected_input}")
            return True

    # ---------------------------------------------------------
    # OPEN INPUT PORT
    # ---------------------------------------------------------
    def open_input(self):
        """Otvorí vstupný MIDI port (bezpečne)."""
        with self._lock:
            if not self.selected_input:
                Logger.warning("DeviceManager: No device selected.")
                return None

            # Ak už je otvorený, zatvoríme ho
            if self.input_port:
                try:
                    self.input_port.close()
                except Exception:
                    pass
                self.input_port = None

            try:
                self.input_port = mido.open_input(self.selected_input)
                Logger.info(f"DeviceManager: Opened input port → {self.selected_input}")
                return self.input_port
            except Exception as e:
                Logger.error(f"DeviceManager: Failed to open port: {e}")
                self._publish_error(f"Failed to open MIDI port: {e}")
                self.input_port = None
                return None

    # ---------------------------------------------------------
    # CLOSE INPUT PORT
    # ---------------------------------------------------------
    def close_input(self) -> None:
        """Zatvorí vstupný port, ak je otvorený."""
        with self._lock:
            if self.input_port:
                try:
                    self.input_port.close()
                    Logger.info("DeviceManager: Port closed.")
                except Exception as e:
                    Logger.error(f"DeviceManager: Error closing port: {e}")
                finally:
                    self.input_port = None

    # ---------------------------------------------------------
    # ERROR PUBLISHING
    # ---------------------------------------------------------
    def _publish_error(self, message: str):
        if self.event_bus:
            try:
                self.event_bus.publish(ERROR_OCCURRED, message)
            except Exception:
                pass

    # ---------------------------------------------------------
    # NO-OP API (UI kompatibilita)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
