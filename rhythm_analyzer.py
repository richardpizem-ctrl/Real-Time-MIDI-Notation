# =========================================================
# RhythmAnalyzer v2.0.0
# Stabilný real‑time analyzátor rytmu pre MIDI note_on udalosti
# =========================================================

import time
from collections import deque
from core.logger import Logger


class RhythmAnalyzer:
    """
    RhythmAnalyzer (v2.0.0)
    -----------------------
    Stabilný analyzátor rytmu pre real‑time MIDI vstup.

    Funkcie:
        - sleduje intervaly medzi note_on udalosťami
        - odhaduje BPM (20–300)
        - resetuje BPM po dlhom tichu
        - odstraňuje extrémne intervaly
        - poskytuje ukazovateľ stability rytmu (0–1)
        - real‑time safe (žiadne výnimky nesmú preraziť)
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
        """Spracuje MIDI event a aktualizuje rytmickú analýzu."""
        try:
            if not isinstance(event, dict):
                Logger.warning(f"RhythmAnalyzer: invalid event {event}")
                return

            if event.get("type") != "note_on":
                return

            event_time = event.get("time") or time.time()

            # Reset BPM po dlhom tichu
            if self.last_event_time is not None:
                silence = event_time - self.last_event_time
                if silence > self.silence_timeout:
                    self.intervals.clear()
                    self.current_bpm = None
                    self.last_event_time = event_time
                    return  # prvý úder po tichu nepočítame

            # Výpočet intervalu
            if self.last_event_time is not None:
                interval = event_time - self.last_event_time

                # Ochrana pred extrémnymi intervalmi
                if 0.02 < interval < 3.0:
                    self.intervals.append(interval)
                    self._update_bpm()

            self.last_event_time = event_time

        except Exception as e:
            Logger.error(f"RhythmAnalyzer: process_midi_event error: {e}")

    # ---------------------------------------------------------
    # BPM CALCULATION
    # ---------------------------------------------------------
    def _update_bpm(self):
        """Prepočíta BPM na základe priemerného intervalu."""
        try:
            if not self.intervals:
                self.current_bpm = None
                return

            avg_interval = sum(self.intervals) / len(self.intervals)

            if avg_interval > 0:
                bpm = 60.0 / avg_interval
                bpm = max(20.0, min(300.0, bpm))  # clamp
                self.current_bpm = bpm
            else:
                self.current_bpm = None

        except Exception as e:
            Logger.error(f"RhythmAnalyzer: BPM calculation error: {e}")
            self.current_bpm = None

    # ---------------------------------------------------------
    # GET BPM
    # ---------------------------------------------------------
    def get_bpm(self):
        """Vráti aktuálne odhadované BPM (alebo None)."""
        return self.current_bpm

    # ---------------------------------------------------------
    # STABILITY
    # ---------------------------------------------------------
    def get_stability(self):
        """
        Jednoduchý ukazovateľ stability rytmu (0–1).
        Používa varianciu intervalov.
        """
        try:
            if len(self.intervals) < 3:
                return None

            avg = sum(self.intervals) / len(self.intervals)
            variance = sum((x - avg) ** 2 for x in self.intervals) / len(self.intervals)

            stability = 1.0 / (1.0 + variance * 50.0)
            return max(0.0, min(1.0, stability))

        except Exception as e:
            Logger.error(f"RhythmAnalyzer: stability calc error: {e}")
            return None
