"""
stream_handler.py – Real-time MIDI Stream Handler (FÁZA 5)

Poskytuje:
- bezpečné čítanie MIDI eventov
- ochranu pred None objektmi
- ochranu pred nevalidnými MIDI dátami
- burst‑safe spracovanie (limit správ na cyklus)
- fallback pri chýbajúcom zariadení
- bezpečné logovanie bez pádu
- čistý shutdown (stop())
"""

import time
import pygame.midi
from typing import Optional, Dict, Any


class StreamHandler:
    """
    Stabilizovaný Real-time MIDI Stream Handler (FÁZA 5).
    """

    def __init__(self, ui_manager=None, event_router=None, perf=None):
        self.ui = ui_manager
        self.event_router = event_router
        self.perf = perf
        self.midi_input = None
        self.running = True

        # -----------------------------------------------------
        # INIT MIDI
        # -----------------------------------------------------
        try:
            pygame.midi.init()
        except Exception as e:
            print(f"[StreamHandler] MIDI init error: {e}")
            return

        # -----------------------------------------------------
        # GET DEFAULT DEVICE
        # -----------------------------------------------------
        try:
            default_id = pygame.midi.get_default_input_id()
        except Exception as e:
            print(f"[StreamHandler] MIDI device lookup error: {e}")
            return

        if default_id == -1:
            print("[StreamHandler] Žiadne MIDI zariadenie nebolo nájdené.")
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
    # CLEAN SHUTDOWN
    # ---------------------------------------------------------
    def stop(self):
        """Bezpečné ukončenie MIDI vstupu."""
        self.running = False

        try:
            if self.midi_input:
                self.midi_input.close()
        except Exception:
            pass

        try:
            pygame.midi.quit()
        except Exception:
            pass

        print("[StreamHandler] Shutdown OK")

    # ---------------------------------------------------------
    # POLLING (BURST-SAFE)
    # ---------------------------------------------------------
    def poll(self, max_messages: int = 64) -> None:
        """
        Bezpečné čítanie MIDI eventov.
        max_messages = limit správ na jeden cyklus (burst-safe).
        """
        if not self.running:
            return

        if self.midi_input is None:
            return

        # Poll
        try:
            if not self.midi_input.poll():
                return
        except Exception as e:
            print(f"[StreamHandler] MIDI poll error: {e}")
            return

        # Read (max 32 naraz)
        try:
            events = self.midi_input.read(32)
        except Exception as e:
            print(f"[StreamHandler] MIDI read error: {e}")
            return

        # Stuck‑poll protection
        if not events:
            return

        # -----------------------------------------------------
        # BURST-SAFE LIMIT
        # -----------------------------------------------------
        if len(events) > max_messages:
            events = events[:max_messages]

        # -----------------------------------------------------
        # PROCESS EVENTS
        # -----------------------------------------------------
        for event in events:
            if not isinstance(event, (list, tuple)) or len(event) != 2:
                print(f"[StreamHandler] Nevalidný MIDI event: {event}")
                continue

            data, timestamp_raw = event

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
                continue

            # -------------------------------------------------
            # BUILD EVENT DICT (timestamp = perf_counter)
            # -------------------------------------------------
            midi_event: Dict[str, Any] = {
                "type": event_type,
                "status": status,
                "note": note,
                "velocity": velocity,
                "channel": channel,
                "time": time.perf_counter()
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
