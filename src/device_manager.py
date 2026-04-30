# device_manager.py – MIDI Device Manager

import mido
from ..core.logger import Logger


class DeviceManager:
    def __init__(self):
        self.devices = []
        self.selected_device = None
        Logger.info("DeviceManager initialized.")

    # ---------------------------------------------------------
    # SCAN DEVICES
    # ---------------------------------------------------------
    def scan_devices(self):
        """Scan available MIDI input devices."""
        try:
            # Strip whitespace – niektoré drivery vracajú trailing spaces
            self.devices = [d.strip() for d in mido.get_input_names()]

            if not self.devices:
                Logger.info("No MIDI devices found.")
            else:
                Logger.info(f"Found MIDI devices: {self.devices}")

            return self.devices

        except Exception as e:
            Logger.error(f"Device scan error: {e}")
            self.devices = []
            return []

    # ---------------------------------------------------------
    # SELECT DEVICE
    # ---------------------------------------------------------
    def select_device(self, device_name):
        """Select a MIDI device by name."""
        try:
            if not self.devices:
                self.scan_devices()

            if device_name not in self.devices:
                Logger.error(f"Device '{device_name}' not found.")
                return None

            # Pretypovanie pre robustnosť
            self.selected_device = str(device_name)

            Logger.info(f"Selected MIDI device: {self.selected_device}")
            return self.selected_device

        except Exception as e:
            Logger.error(f"Device selection error: {e}")
            return None

    # ---------------------------------------------------------
    # OPEN DEVICE
    # ---------------------------------------------------------
    def open_selected(self):
        """Open the selected MIDI device for input."""
        try:
            if not self.selected_device:
                Logger.error("No MIDI device selected.")
                return None

            try:
                port = mido.open_input(self.selected_device)
            except IOError:
                Logger.error("Device busy or locked by another application.")
                return None

            Logger.info(f"MIDI device opened: {self.selected_device}")
            return port

        except Exception as e:
            Logger.error(f"Failed to open MIDI device: {e}")
            return None
