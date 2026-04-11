"""
stream_handler.py – Real-time MIDI Stream Handler (FÁZA 4)

Poskytuje:
- bezpečné čítanie MIDI eventov
- ochranu pred None objektmi
- ochranu pred nevalidnými MIDI dátami
- fallback pri chýbajúcom zariadení
- bezpečné logovanie bez pádu
"""

import time
import pygame.midi
from typing import Optional, Dict, Any


class StreamHandler:
    """
    Stabilizovaný Real-time MIDI Stream Handler.
    """

    def __init__(self, ui_manager=None, event_router=None, perf=None):
        self.ui = ui_manager
        self.event_router = event_router
        self.perf = perf

        # -----------------------------------------------------
        # INIT MIDI
        # -----------------------------------------------------
        try:
            pygame.midi.init()
        except Exception as e:
            print(f"[StreamHandler] MIDI init error: {e}")
            self.midi_input = None
            return

        # -----------------------------------------------------
        # GET DEFAULT DEVICE
        # -----------------------------------------------------
        try:
            default_id = pygame.midi.get_default_input_id()
        except Exception as e:
            print(f"[StreamHandler] MIDI device lookup error: {e}")
            self.midi_input = None
            return

        if default_id == -1:
            print("[StreamHandler] Žiadne MIDI zariadenie nebolo nájdené.")
            self.midi_input = None
            return

        # -----------------------------------------------------
        # OPEN DEVICE
        # -----------------------------------------------------
        try:
            self.midi_input = pygame.midi.Input(default_id)
            print(f"[StreamHandler] MIDI Input otvorený: {default_id}")
        except Exception as e:
            print(f"[StreamHandler] MIDI Input error: {e}")
            self.midi_input = None

    # ---------------------------------------------------------
    # POLLING
    # ---------------------------------------------------------
    def poll(self) -> None:
        """Bezpečné čítanie MIDI eventov."""
        if self.midi_input is None:
            return

        # Poll
        try:
            if not self.midi_input.poll():
                return
        except Exception as e:
            print(f"[StreamHandler] MIDI poll error: {e}")
            return

        # Read
        try:
            events = self.midi_input.read(32)
        except Exception as e:
            print(f"[StreamHandler] MIDI read error: {e}")
            return

        # -----------------------------------------------------
        # PROCESS EVENTS
        # -----------------------------------------------------
        for event in events:
            if not isinstance(event, (list, tuple)) or len(event) != 2:
                print(f"[StreamHandler] Nevalidný MIDI event: {event}")
                continue

            data, timestamp = event

            if not isinstance(data, (list, tuple)) or len(data) < 3:
                print(f"[StreamHandler] Nevalidné MIDI dáta: {data}")
                continue

            pipeline_start = time.perf_counter()

            # -------------------------------------------------
            # PARSE MIDI MESSAGE
            # -------------------------------------------------
            try:
                status = int(data[0])
                note = int(data[1])
                velocity = int(data[2])
            except Exception:
                print(f"[StreamHandler] Nevalidné MIDI hodnoty: {data}")
                continue

            channel = status & 0x0F
            status_type = status & 0xF0

            # Determine event type
            if status_type == 0x90 and velocity > 0:
                event_type = "note_on"
            elif status_type == 0x90 and velocity == 0:
                event_type = "note_off"
            elif status_type == 0x80:
                event_type = "note_off"
            elif status_type == 0xB0:
                event_type = "control_change"
            else:
                print(f"[StreamHandler] Neznámy MIDI status: {status}")
                continue

            # -------------------------------------------------
            # BUILD EVENT DICT
            # -------------------------------------------------
            midi_event: Dict[str, Any] = {
                "type": event_type,
                "status": status,
                "note": note,
                "velocity": velocity,
                "channel": channel,
                "time": timestamp
            }

            # -------------------------------------------------
            # ROUTE EVENT
            # -------------------------------------------------
            try:
                if self.event_router:
                    self.event_router.route(midi_event)
            except Exception as e:
                print(f"[StreamHandler] EventRouter error: {e}")

            # -------------------------------------------------
            # LATENCY TRACKING
            # -------------------------------------------------
            pipeline_end = time.perf_counter()
            latency_ms = (pipeline_end - pipeline_start) * 1000.0

            try:
                if self.perf and hasattr(self.perf, "record_event_latency"):
                    self.perf.record_event_latency(latency_ms)
            except Exception as e:
                print(f"[StreamHandler] PerfTracker error: {e}")
