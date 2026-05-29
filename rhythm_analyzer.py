# =========================================================
# RhythmAnalyzer v4.3.0
# Stable real‑time rhythm analyzer for MIDI note_on events
# =========================================================

import time
from collections import deque
from core.logger import Logger


class RhythmAnalyzer:
    """
    RhythmAnalyzer (v4.3.0)
    -----------------------
    Stable real‑time rhythm analyzer for MIDI input.

    Features:
        - tracks intervals between note_on events
        - estimates BPM (20–300)
        - resets BPM after silence
        - trims extreme intervals
        - provides rhythm stability (0–1)
        - real‑time safe (no exceptions)
        - clean English API
        - ready for future groove/swing analysis
    """

    def __init__(self, max_events: int = 32, silence_timeout: float = 2.0):
        self.intervals = deque(maxlen=max_events)
        self.last_event_time = None
        self.current_bpm = None
        self.silence_timeout = float(silence_timeout)

    # ---------------------------------------------------------
    # PROCESS MIDI EVENT
    # ---------------------------------------------------------
    def process_midi_event(self, event):
        """Process a MIDI event and update rhythm analysis."""
        try:
            if not isinstance(event, dict):
                Logger.warning(f"RhythmAnalyzer: invalid event {event}")
                return

            if event.get("type") != "note_on":
                return

            event_time = event.get("time") or time.time()

            # Silence reset
            if self.last_event_time is not None:
                silence = event_time - self.last_event_time
                if silence > self.silence_timeout:
                    self.intervals.clear()
                    self.current_bpm = None
                    self.last_event_time = event_time
                    return

            # Interval calculation
            if self.last_event_time is not None:
                interval = event_time - self.last_event_time

                # Valid interval range
                if 0.02 < interval < 3.0:
                    self.intervals.append(interval)
                    self._update_bpm()

            self.last_event_time = event_time

        except Exception:
            try:
                Logger.error("RhythmAnalyzer: process_midi_event failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # BPM CALCULATION
    # ---------------------------------------------------------
    def _update_bpm(self):
        """Recalculate BPM based on average interval."""
        try:
            if not self.intervals:
                self.current_bpm = None
                return

            avg_interval = sum(self.intervals) / len(self.intervals)

            if avg_interval > 0:
                bpm = 60.0 / avg_interval
                self.current_bpm = max(20.0, min(300.0, bpm))
            else:
                self.current_bpm = None

        except Exception:
            try:
                Logger.error("RhythmAnalyzer: BPM calculation failure")
            except Exception:
                pass
            self.current_bpm = None

    # ---------------------------------------------------------
    # GET BPM
    # ---------------------------------------------------------
    def get_bpm(self):
        """Return current BPM estimate (or None)."""
        return self.current_bpm

    # ---------------------------------------------------------
    # STABILITY
    # ---------------------------------------------------------
    def get_stability(self):
        """Return rhythm stability (0–1) based on interval variance."""
        try:
            if len(self.intervals) < 3:
                return None

            avg = sum(self.intervals) / len(self.intervals)
            variance = sum((x - avg) ** 2 for x in self.intervals) / len(self.intervals)

            stability = 1.0 / (1.0 + variance * 50.0)
            return max(0.0, min(1.0, stability))

        except Exception:
            try:
                Logger.error("RhythmAnalyzer: stability calculation failure")
            except Exception:
                pass
            return None
