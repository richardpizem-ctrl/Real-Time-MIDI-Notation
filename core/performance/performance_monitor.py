# =========================================================
# performance_monitor.py v4.3.0
# Ultra-light real-time performance monitor
# =========================================================

from __future__ import annotations
import time


class PerformanceMonitor:
    """
    PerformanceMonitor (v4.3.0)
    ---------------------------
    Ultra-light performance tracker for real-time rendering.

    Tracks:
        - FPS (smoothed)
        - frame time (ms)
        - CPU frame duration
        - real-time safe (no exceptions)
        - zero allocations in hot path
        - __slots__ for ultra-low latency
    """

    __slots__ = (
        "_last_time",
        "_fps",
        "_alpha",
        "_frame_time_ms",
    )

    def __init__(self, smoothing: float = 0.10):
        """
        :param smoothing: smoothing factor for FPS EMA (0.05–0.3 recommended)
        """
        self._last_time = time.perf_counter()
        self._fps = 0.0
        self._alpha = float(smoothing)
        self._frame_time_ms = 0.0

    # ---------------------------------------------------------
    # UPDATE PER FRAME
    # ---------------------------------------------------------
    def update(self) -> None:
        """Call once per frame. Real-time safe."""
        try:
            now = time.perf_counter()
            dt = now - self._last_time
            self._last_time = now

            # Frame time in ms
            self._frame_time_ms = dt * 1000.0

            # FPS smoothing (EMA)
            if dt > 0:
                current_fps = 1.0 / dt
                a = self._alpha
                self._fps = (1 - a) * self._fps + a * current_fps if self._fps > 0 else current_fps

        except Exception:
            # Never break real-time loop
            pass

    # ---------------------------------------------------------
    # GETTERS
    # ---------------------------------------------------------
    def get_fps(self) -> float:
        """Return smoothed FPS."""
        return self._fps

    def get_frame_time_ms(self) -> float:
        """Return last frame time in milliseconds."""
        return self._frame_time_ms

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------
    def reset(self) -> None:
        """Reset internal timing state."""
        try:
            self._last_time = time.perf_counter()
            self._fps = 0.0
            self._frame_time_ms = 0.0
        except Exception:
            pass
