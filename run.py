from notation_engine.notation_processor import NotationProcessor

def main():
    processor = NotationProcessor()

    # Testovací MIDI event
    test_event = {
        "type": "note_on",
        "note": 60,
        "velocity": 100,
        "time": 0.5
    }

    processor.process_midi_event(test_event)

if __name__ == "__main__":
    main()

