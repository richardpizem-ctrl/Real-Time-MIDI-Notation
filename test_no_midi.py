# Test behu systému bez MIDI zariadení

from device_manager import DeviceManager
from notation_engine.notation_processor import NotationProcessor

def main():
    print("=== TEST: NO MIDI DEVICES ===")

    dm = DeviceManager()
    np = NotationProcessor()

    devices = dm.list_devices()

    if not devices:
        print("[TEST] Neboli nájdené žiadne MIDI zariadenia – OK")
    else:
        print("[TEST] MIDI zariadenia nájdené:", devices)

    # Simulovaný MIDI event (bez reálneho zariadenia)
    fake_event = {
        "type": "note_on",
        "note": 64,
        "velocity": 90,
        "time": None
    }

    print("[TEST] Spracovávam simulovaný MIDI event...")
    np.process_midi_event(fake_event)

    print("[TEST] Test úspešne dokončený.")

if __name__ == "__main__":
    main()
