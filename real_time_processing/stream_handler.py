import time
import pygame.midi


class StreamHandler:
    """
    Real-time MIDI Stream Handler
    --------------------------------
    - Číta MIDI eventy z default input zariadenia
    - Posiela ich do EventRoutera
    - Posiela ich do PianoRollUI
    - Meria pipeline latency (čas spracovania jedného eventu)
    - Meria event processing time
    - Meria UI processing time
    - Prepojené s PerformanceTracker (FPS/CPU/Latency grafy)
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

        # Prečítaj batch eventov
        events = self.midi_input.read(32)

        for data, timestamp in events:

            pipeline_start = time.perf_counter()

            status = data[0]
            note = data[1]
            velocity = data[2]

            midi_event = {
                "status": status,
                "note": note,
                "velocity": velocity,
                "timestamp": timestamp
            }

            # -----------------------------
            # 1) ROUTING
            # -----------------------------
            event_start = time.perf_counter()

            if self.event_router:
                try:
                    self.event_router.route(midi_event)
                except Exception as e:
                    print(f"❌ EventRouter error: {e}")

            event_end = time.perf_counter()
            event_processing_ms = (event_end - event_start) * 1000.0

            # -----------------------------
            # 2) UI UPDATE
            # -----------------------------
            ui_start = time.perf_counter()

            if self.piano_roll_ui:
                try:
                    self.piano_roll_ui.handle_midi_event(midi_event)
                except Exception as e:
                    print(f"❌ PianoRollUI error: {e}")

            ui_end = time.perf_counter()
            ui_processing_ms = (ui_end - ui_start) * 1000.0

            # -----------------------------
            # 3) PIPELINE LATENCY
            # -----------------------------
            pipeline_end = time.perf_counter()
            pipeline_latency_ms = (pipeline_end - pipeline_start) * 1000.0

            # -----------------------------
            # 4) PERFORMANCE TRACKER
            # -----------------------------
            if self.perf:

                # celková latencia eventu
                if hasattr(self.perf, "record_event_latency"):
                    self.perf.record_event_latency(pipeline_latency_ms)

                # detailné metriky pre debug overlay
                if hasattr(self.perf, "record_pipeline_step"):
                    self.perf.record_pipeline_step(
                        event_processing_ms,
                        ui_processing_ms,
                        pipeline_latency_ms
                    )

    # ---------------------------------------------------------
    # UKONČENIE
    # ---------------------------------------------------------
    def close(self):
        if self.midi_input:
            self.midi_input.close()
        pygame.midi.quit()
