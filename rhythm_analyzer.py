# Analýza rytmu pre real-time MIDI notáciu
import time
from collections import deque

class RhythmAnalyzer:
    """
    Vylepšený analyzátor rytmu:
    - sleduje čas medzi note_on udalosťami
    - odhaduje tempo (BPM)
    - sleduje stabilitu rytmu
    - chráni pred extrémnymi intervalmi
    - resetuje BPM po dlhom tichu
    """

    def __init__(self, max_events: int = 32, silence_timeout: float = 2.0):
        self.intervals = deque(maxlen=max_events)
        self.last_event_time = None
        self.current_bpm = None
        self.silence_timeout = silence_timeout

    def process_midi_event(self, event):
        """Spracuje MIDI event a aktualizuje rytmickú analýzu."""
        if event.get("type") != "note_on":
            return

        event_time = event.get("time") or time.time()

        # Reset BPM pri dlhom tichu
        if self.last_event_time is not None:
            if event_time - self.last_event_time > self.silence_timeout:
                self.intervals.clear()
                self.current_bpm = None

        # Výpočet intervalu
        if self.last_event_time is not None:
            interval = event_time - self.last_event_time

            # Ochrana pred extrémnymi intervalmi
            if 0.02 < interval < 3.0:  # 20 ms – 3 s
                self.intervals.append(interval)
                self._update_bpm()

        self.last_event_time = event_time

    def _update_bpm(self):
        """Prepočíta BPM na základe priemerného intervalu."""
        if not self.intervals:
            self.current_bpm = None
            return

        avg_interval = sum(self.intervals) / len(self.intervals)

        if avg_interval > 0:
            bpm = 60.0 / avg_interval

            # Clamp BPM do realistického rozsahu
            bpm = max(20.0, min(300.0, bpm))

            self.current_bpm = bpm
        else:
            self.current_bpm = None

    def get_bpm(self):
        """Vráti aktuálne odhadované BPM (alebo None)."""
        return self.current_bpm

    def get_stability(self):
        """
        Jednoduchý ukazovateľ stability rytmu (0–1).
        Používa varianciu intervalov.
        """
        if len(self.intervals) < 3:
            return None

        avg = sum(self.intervals) / len(self.intervals)
        variance = sum((x - avg) ** 2 for x in self.intervals) / len(self.intervals)

        stability = 1.0 / (1.0 + variance * 50.0)
        return max(0.0, min(1.0, stability))
