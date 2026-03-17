# Rhythm Analyzer – determines note durations and rhythmic values

from ..core.logger import Logger

class RhythmAnalyzer:
    def __init__(self, tempo_bpm=120):
        self.tempo_bpm = tempo_bpm
        self.ms_per_beat = 60000 / tempo_bpm
        Logger.info(f"RhythmAnalyzer initialized at {tempo_bpm} BPM.")

    def analyze(self, note_events):
        """
        Takes a list of note events with timestamps and returns
        their rhythmic durations (quarter, eighth, sixteenth, etc.)
        """
        analyzed = []

        try:
            for i in range(len(note_events) - 1):
                current = note_events[i]
                next_event = note_events[i + 1]

                duration_ms = next_event["timestamp"] - current["timestamp"]
                beats = duration_ms / self.ms_per_beat

                rhythmic_value = self._quantize(beats)

                analyzed.append({
                    "note": current["note"],
                    "octave": current["octave"],
                    "duration_beats": beats,
                    "rhythm": rhythmic_value
                })

            return analyzed

        except Exception as e:
            Logger.error(f"RhythmAnalyzer error: {e}")
            return []

    def _quantize(self, beats):
        """Quantize beat duration to nearest musical value."""
        values = {
            1.0: "quarter",
            0.5: "eighth",
            0.25: "sixteenth",
            2.0: "half",
            4.0: "whole"
        }

        closest = min(values.keys(), key=lambda x: abs(x - beats))
        return values[closest]

