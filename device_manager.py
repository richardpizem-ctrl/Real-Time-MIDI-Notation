# =========================================================
# DeviceManager v4.3.0 – Stable MIDI Device Manager
# =========================================================

import threading
import mido
from core.logger import Logger
from core.event_types import ERROR_OCCURRED
from core.event_bus import EventBus


class DeviceManager:
    """
    DeviceManager (v4.3.0)
    ----------------------
    Stable, safe, thread‑safe MIDI Device Manager.

    Features:
        - refresh_devices()
        - list_devices()
        - select_device(index)
        - open_input()
        - close_input()

    Properties:
        - protects against Windows/ASIO locked‑port bug
        - no exceptions leak out
        - EventBus integration
        - ready for future routing upgrades
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
        """Refresh list of available MIDI inputs (thread‑safe)."""
        with self._lock:
            try:
                self.available_inputs = [
                    name.strip() for name in mido.get_input_names()
                ]
                Logger.info(
                    f"DeviceManager: Found {len(self.available_inputs)} MIDI inputs."
                )
            except Exception as e:
                Logger.error(f"DeviceManager: Failed to refresh devices: {e}")
                self.available_inputs = []
                self._publish_error(f"MIDI device scan failed: {e}")

    # ---------------------------------------------------------
    # LIST DEVICES
    # ---------------------------------------------------------
    def list_devices(self) -> list[str]:
        """Return list of available MIDI inputs."""
        with self._lock:
            return list(self.available_inputs)

    # ---------------------------------------------------------
    # SELECT DEVICE
    # ---------------------------------------------------------
    def select_device(self, index: int) -> bool:
        """Select MIDI device by index."""
        with self._lock:
            if not self.available_inputs:
                Logger.warning("DeviceManager: No MIDI devices found.")
                return False

            if not isinstance(index, int) or index < 0 or index >= len(self.available_inputs):
                Logger.warning(f"DeviceManager: Invalid device index {index}.")
                return False

            self.selected_input = str(self.available_inputs[index])
            Logger.info(f"DeviceManager: Selected device → {self.selected_input}")
            return True

    # ---------------------------------------------------------
    # OPEN INPUT PORT
    # ---------------------------------------------------------
    def open_input(self):
        """Open selected MIDI input port safely."""
        with self._lock:
            if not self.selected_input:
                Logger.warning("DeviceManager: No device selected.")
                return None

            # Close existing port if open
            if self.input_port:
                try:
                    self.input_port.close()
                except Exception:
                    pass
                self.input_port = None

            try:
                # Windows/ASIO bug: port may be locked
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
        """Close input port if open."""
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
    # NO-OP API (UI compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
