"""
latency_monitor.py – Real-time latency monitoring (FÁZA 4)

Poskytuje:
- bezpečné meranie latencie medzi udalosťami
- ochranu pred None a nevalidnými hodnotami
- stabilné štatistiky (min, max, avg, last)
- odolnosť voči chybám v real-time pipeline
"""

import time
from typing import Optional, Dict, Any
from ..core.logger import Logger


class LatencyMonitor:
    """
    Simple real-time latency monitor.
    Measures time between events and provides basic statistics.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize latency monitor with sliding window.
        Ensures window_size is valid and logs initialization.
        """
        try:
            self.window_size = max(1, int(window_size))
        except Exception:
            self.window_size = 100

        self.reset()

        try:
            Logger.info(f"LatencyMonitor initialized (window_size={self.window_size}).")
        except Exception:
            print(f"LatencyMonitor initialized (window_size={self.window_size}). Logger failed.")

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------
    def reset(self) -> None:
        """Reset all latency statistics."""
        self.last_timestamp: Optional[float] = None
        self.latencies: list[float] = []
        self.max_latency: float = 0.0
        self.min_latency: Optional[float] = None
        self.avg_latency: float = 0.0

    # ---------------------------------------------------------
    # RECORD EVENT
    # ---------------------------------------------------------
    def record_event(self) -> Optional[float]:
        """
        Record a new event timestamp and update latency statistics.
        Returns:
            float | None – last measured latency in seconds
        """
        now = time.time()

        # First event → no latency yet
        if self.last_timestamp is None:
            self.last_timestamp = now
            return None

        latency = now - self.last_timestamp
        self.last_timestamp = now

        try:
            self.latencies.append(latency)

            # Sliding window
            if len(self.latencies) > self.window_size:
                self.latencies.pop(0)

            # Update stats
            self.max_latency = max(self.max_latency, latency)
            self.min_latency = latency if self.min_latency is None else min(self.min_latency, latency)

            # Safe average
            if self.latencies:
                self.avg_latency = sum(self.latencies) / len(self.latencies)

        except Exception as e:
            try:
                Logger.error(f"LatencyMonitor.record_event error: {e}")
            except Exception:
                print(f"LatencyMonitor.record_event error: {e} (Logger failed)")

        return latency

    # ---------------------------------------------------------
    # GET STATS
    # ---------------------------------------------------------
    def get_stats(self) -> Dict[str, Any]:
        """
        Return current latency statistics as a dict:
        {
            'last': float | None,
            'avg': float | None,
            'min': float | None,
            'max': float | None,
            'count': int
        }
        """
        try:
            last = self.latencies[-1] if self.latencies else None

            return {
                "last": last,
                "avg": self.avg_latency if self.latencies else None,
                "min": self.min_latency,
                "max": self.max_latency if self.latencies else None,
                "count": len(self.latencies),
            }

        except Exception as e:
            try:
                Logger.error(f"LatencyMonitor.get_stats error: {e}")
            except Exception:
                print(f"LatencyMonitor.get_stats error: {e} (Logger failed)")

            return {
                "last": None,
                "avg": None,
                "min": None,
                "max": None,
                "count": 0,
            }
