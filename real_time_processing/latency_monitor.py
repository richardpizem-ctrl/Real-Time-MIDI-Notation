# latency_monitor.py – Real-time latency monitoring

import time
from ..core.logger import Logger


class LatencyMonitor:
    """
    Simple real-time latency monitor.
    Measures time between events and provides basic statistics.
    Stabilizované:
    - ochrana pred None
    - bezpečné výpočty
    - fallback pri chybách
    """

    def __init__(self, window_size=100):
        try:
            self.window_size = max(1, int(window_size))
        except Exception:
            self.window_size = 100

        self.reset()
        Logger.info(f"LatencyMonitor initialized (window_size={self.window_size}).")

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------
    def reset(self):
        """Reset all latency statistics."""
        self.last_timestamp = None
        self.latencies = []
        self.max_latency = 0.0
        self.min_latency = None
        self.avg_latency = 0.0

    # ---------------------------------------------------------
    # RECORD EVENT
    # ---------------------------------------------------------
    def record_event(self):
        """
        Record a new event timestamp and update latency statistics.
        Returns the last measured latency (in seconds) or None if not enough data.
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

            # Keep sliding window
            if len(self.latencies) > self.window_size:
                self.latencies.pop(0)

            # Update stats
            self.max_latency = max(self.max_latency, latency)
            self.min_latency = latency if self.min_latency is None else min(self.min_latency, latency)
            self.avg_latency = sum(self.latencies) / len(self.latencies)

        except Exception as e:
            Logger.error(f"LatencyMonitor.record_event error: {e}")

        return latency

    # ---------------------------------------------------------
    # GET STATS
    # ---------------------------------------------------------
    def get_stats(self):
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
            Logger.error(f"LatencyMonitor.get_stats error: {e}")
            return {
                "last": None,
                "avg": None,
                "min": None,
                "max": None,
                "count": 0,
            }
