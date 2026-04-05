# MIDI správca zariadení
import mido


class DeviceManager:
    """
    Správca MIDI zariadení – zisťuje dostupné porty,
    umožňuje vybrať zariadenie a otvoriť vstupný port.
    """

    def __init__(self):
        self.available_inputs: list[str] = []
        self.selected_input: str | None = None
        self.input_port = None
        self.refresh_devices()

    # ---------------------------------------------------------
    # REFRESH DEVICE LIST
    # ---------------------------------------------------------
    def refresh_devices(self) -> None:
        """Aktualizuje zoznam dostupných MIDI vstupov."""
        try:
            self.available_inputs = mido.get_input_names()
        except Exception as e:
            print(f"[DeviceManager] Chyba pri načítaní MIDI zariadení: {e}")
            self.available_inputs = []

    # ---------------------------------------------------------
    # LIST DEVICES
    # ---------------------------------------------------------
    def list_devices(self) -> list[str]:
        """Vráti zoznam dostupných MIDI vstupov."""
        return self.available_inputs

    # ---------------------------------------------------------
    # SELECT DEVICE
    # ---------------------------------------------------------
    def select_device(self, index: int) -> bool:
        """Vyberie MIDI zariadenie podľa indexu."""
        if not self.available_inputs:
            print("[DeviceManager] Žiadne MIDI zariadenia neboli nájdené.")
            return False

        if index < 0 or index >= len(self.available_inputs):
            print("[DeviceManager] Neplatný index zariadenia.")
            return False

        self.selected_input = self.available_inputs[index]
        print(f"[DeviceManager] Vybrané zariadenie: {self.selected_input}")
        return True

    # ---------------------------------------------------------
    # OPEN INPUT PORT
    # ---------------------------------------------------------
    def open_input(self):
        """Otvorí vstupný MIDI port."""
        if not self.selected_input:
            print("[DeviceManager] Nebolo vybrané žiadne zariadenie.")
            return None

        try:
            self.input_port = mido.open_input(self.selected_input)
            print(f"[DeviceManager] Otvorený vstupný port: {self.selected_input}")
            return self.input_port
        except Exception as e:
            print(f"[DeviceManager] Chyba pri otváraní portu: {e}")
            return None

    # ---------------------------------------------------------
    # CLOSE INPUT PORT
    # ---------------------------------------------------------
    def close_input(self) -> None:
        """Zatvorí vstupný port, ak je otvorený."""
        if self.input_port:
            try:
                self.input_port.close()
                print("[DeviceManager] Port bol zatvorený.")
            except Exception as e:
                print(f"[DeviceManager] Chyba pri zatváraní portu: {e}")
            finally:
                self.input_port = None
