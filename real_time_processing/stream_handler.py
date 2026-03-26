import time
import pygame.midi

class StreamHandler:
    """
    Čistý MIDI Stream Handler pre real-time spracovanie.
    - Číta MIDI eventy z default input zariadenia
    - Posiela ich do EventRoutera
    - Posiela ich do PianoRollUI
    - Meria pipeline latency (čas spracovania jedného eventu)
    """

    def __init__(self, piano_roll_ui=None, event_router=None, perf=None):
        self.piano_roll_ui = piano_roll_ui
        self.event_router = event_router
        self.perf = perf  # PerformanceTracker

        pygame.midi.init()

        # Nájde default MIDI vstup
        default_id = pygame.midi.get_default_input_id()
        if default_id == -1:
            print("⚠️  Žiadne MIDI zariadenie nebolo nájdené.")
            self.midi_input = None
        else:
            self.midi_input = pygame.midi.Input(default_id)
            print(f"🎹 MIDI Input otvorený: {default_id}")

    # ---------------------------------------------------------
    # HLAVNÁ FUNKCIA NA SPRACOVANIE MIDI EVENTOV
    # ---------------------------------------------------------
    def poll(self):
        """
        Spracuje všetky dostupné MIDI eventy.
        Volá sa v hlavnej slučke UIManagera.
        """

        if self.midi_input is None:
            return

        if not self.midi_input.poll():
            return

        events = self.midi_input.read(32)  # batch
        for data, timestamp in events:

            start = time.perf_counter()

            status = data[0]
            note = data[1]
            velocity = data[2]

            midi_event = {
                "status": status,
                "note": note,
                "velocity": velocity,
                "timestamp": timestamp
            }

            # 1) Pošli do EventRoutera
            if self.event_router:
                self.event_router.route(midi_event)

            # 2) Pošli do PianoRollUI
            if self.piano_roll_ui:
                self.piano_roll_ui.handle_midi_event(midi_event)

            # 3) Pipeline latency
            end = time.perf_counter()
            latency_ms = (end - start) * 1000.0

            if self.perf:
                self.perf.record_event_latency(latency_ms)

    # ---------------------------------------------------------
    # UKONČENIE
    # ---------------------------------------------------------
    def close(self):
        if self.midi_input:
            self.midi_input.close()
        pygame.midi.quit()
