import time
import pygame.midi


class StreamHandler:
    """
    Real-time MIDI Stream Handler
    --------------------------------
    - Číta MIDI eventy z default input zariadenia
    - Posiela ich do EventRoutera
    - Prepojené s UIManagerom
    - Prepojené s NotationProcessorom
    - Meria pipeline latency
    - Prepojené s PerformanceTracker
    """

    def __init__(self, ui_manager=None, event_router=None, perf=None):
        self.ui = ui_manager
        self.event_router = event_router
        self.perf = perf  # PerformanceTracker

        pygame.midi.init()

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
        Volá sa v hlavnej slučke run.py.
        """

        if self.midi_input is None:
            return

        if not self.midi_input.poll():
            return

        events = self.midi_input.read(32)

        for data, timestamp in events:

            pipeline_start = time.perf_counter()

            status = data[0]
            note = data[1]
            velocity = data[2]

            # MIDI status → event_type + channel
            event_type = None
            channel = status & 0x0F
            status_type = status & 0xF0

            if status_type == 0x90 and velocity > 0:
                event_type = "note_on"
            elif status_type == 0x90 and velocity == 0:
                event_type = "note_off"
            elif status_type == 0x80:
                event_type = "note_off"
            elif status_type == 0xB0:
                event_type = "control_change"

            midi_event = {
                "type": event_type,
                "status": status,
                "note": note,
                "velocity": velocity,
                "channel": channel,
                "timestamp": timestamp
            }

            # -----------------------------
            # 1) ROUTING DO EventRoutera
            # -----------------------------
            event_start = time.perf_counter()

            if self.event_router and event_type:
                try:
                    self.event_router.route(midi_event)
                except Exception as e:
                    print(f"❌ EventRouter error: {e}")

            event_end = time.perf_counter()
            event_processing_ms = (event_end - event_start) * 1000.0

            # -----------------------------
            # 2) PIPELINE LATENCY
            # -----------------------------
            pipeline_end = time.perf_counter()
            pipeline_latency_ms = (pipeline_end - pipeline_start) * 1000.0

            # -----------------------------
            # 3) PERFORMANCE TRACKER
            # -----------------------------
            if self.perf:

                if hasattr(self.perf, "record_event_latency"):
                    self.perf.record_event_latency(pipeline_latency_ms)

                if hasattr(self.perf, "record_pipeline_step"):
                    self.perf.record_pipeline_step(
                        event_processing_ms,
                        0.0  # UI čas už nesledujeme tu
                    )
