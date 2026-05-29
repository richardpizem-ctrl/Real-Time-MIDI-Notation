# =========================================================
# LatencyMonitor v4.3.0
# Stabilné meranie latencie pre real-time processing
# - mikrooptimalizácie
# - žiadne alokácie v slučke
# - real-time safe
# - diagnostické fallbacky
# =========================================================

import time
from collections import deque
from typing import Optional, Dict, Any
from ..core.logger import Logger


class LatencyMonitor:
    """
    LatencyMonitor (v4.3.0):
    - bezpečné meranie latencie medzi udalosťami
    - stabilné štatistiky (min, max, avg, last)
    - odolnosť voči chybám v real-time pipeline
    - optimalizované pre architektúru v4.3.0
    - žiadne alokácie v slučke
    """

    __slots__ = (
        "window_size",
        "last_timestamp",
        "latencies",
        "max_latency",
        "min_latency",
        "avg_latency",
    )

    def __init__(self, window_size: int = 100):
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
        self.latencies: deque[float] = deque(maxlen=self.window_size)
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
        now = time.perf_counter()

        # First event → no latency yet
        last = self.last_timestamp
        if last is None:
            self.last_timestamp = now
            return None

        latency = now - last
        self.last_timestamp = now

        try:
            self.latencies.append(latency)

            # Update stats
            if latency > self.max_latency:
                self.max_latency = latency

            if self.min_latency is None or latency < self.min_latency:
                self.min_latency = latency

            count = len(self.latencies)
            if count:
                # Avoid sum() allocation by manual incremental update
                self.avg_latency = (
                    (self.avg_latency * (count - 1)) + latency
                ) / count

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
        Return current latency statistics:
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
