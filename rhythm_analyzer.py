# Analýza rytmu pre real-time MIDI notáciu
import time
from collections import deque

class RhythmAnalyzer:
    """
    Jednoduchý analyzátor rytmu:
    - sleduje čas medzi note_on udalosťami
    - odhaduje tempo (BPM)
    - sleduje stabilitu rytmu
    """

    def __init__(self, max_events: int = 32):
        # Ukladáme časové rozdiely medzi po sebe idúcimi note_on
        self.intervals = deque(maxlen=max_events)
        self.last_event_time = None
        self.current_bpm = None

    def process_midi_event(self, event):
        """
        Spracuje MIDI event a aktualizuje rytmickú analýzu.
        Očakáva dict s kľúčmi:
        - type: "note_on" / "note_off" / ...
        - time: čas v sekundách (alebo None → použije sa time.time())
        """
        if event.get("type") != "note_on":
            return

        event_time = event.get("time")
        if event_time is None:
            event_time = time.time()

        if self.last_event_time is not None:
            interval = event_time - self.last_event_time
            if interval > 0:
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
            self.current_bpm = 60.0 / avg_interval
        else:
            self.current_bpm = None

    def get_bpm(self):
        """Vráti aktuálne odhadované BPM (alebo None)."""
        return self.current_bpm

    def get_stability(self):
        """
        Vráti jednoduchý ukazovateľ stability rytmu (0–1),
        kde 1 = veľmi stabilný, 0 = veľmi rozbitý.
        """
        if len(self.intervals) < 3:
            return None

        avg = sum(self.intervals) / len(self.intervals)
        variance = sum((x - avg) ** 2 for x in self.intervals) / len(self.intervals)
        # hrubá normalizácia – čím menšia variancia, tým vyššia stabilita
        stability = 1.0 / (1.0 + variance * 50.0)
        return max(0.0, min(1.0, stability))
