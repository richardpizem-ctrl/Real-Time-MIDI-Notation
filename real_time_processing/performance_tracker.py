# =========================================================
# PerformanceTracker v4.3.0
# Stabilné meranie FPS, latency, throughput a CPU load
# pre Real-Time-MIDI-Notation
# =========================================================

import time
import collections
from typing import Optional, Dict, Any

try:
    import psutil
except ImportError:
    psutil = None


class PerformanceTracker:
    """
    PerformanceTracker (v4.3.0):
    - FPS / frame time
    - render time
    - MIDI latency
    - event throughput
    - pipeline latency (event/UI/total)
    - CPU usage (ak psutil dostupný)
    - žiadne alokácie v slučke
    - real-time safe
    """

    __slots__ = (
        "frame_times", "last_frame_start",
        "render_times", "last_render_start",
        "midi_latencies", "last_midi_event_time",
        "event_intervals", "last_event_time",
        "event_processing_times", "ui_processing_times",
        "pipeline_latencies",
        "process"
    )

    def __init__(self, history_size: int = 300):
        try:
            history_size = max(1, int(history_size))
        except Exception:
            history_size = 300

        # FRAME TIME (FPS)
        self.frame_times = collections.deque(maxlen=history_size)
        self.last_frame_start = None

        # RENDER TIME
        self.render_times = collections.deque(maxlen=history_size)
        self.last_render_start = None

        # MIDI LATENCY
        self.midi_latencies = collections.deque(maxlen=history_size)
        self.last_midi_event_time = None

        # EVENT THROUGHPUT
        self.event_intervals = collections.deque(maxlen=history_size)
        self.last_event_time = None

        # PIPELINE METRICS
        self.event_processing_times = collections.deque(maxlen=history_size)
        self.ui_processing_times = collections.deque(maxlen=history_size)
        self.pipeline_latencies = collections.deque(maxlen=history_size)

        # CPU
        if psutil is not None:
            try:
                self.process = psutil.Process()
            except Exception:
                self.process = None
        else:
            self.process = None

    # ---------------------------------------------------------
    # INTERNAL SAFE INTERVAL RECORDER
    # ---------------------------------------------------------
    @staticmethod
    def _record_interval(start: Optional[float], target_deque: collections.deque) -> None:
        if start is None:
            return
        try:
            target_deque.append(time.perf_counter() - start)
        except Exception:
            pass

    # ---------------------------------------------------------
    # FRAME / FPS
    # ---------------------------------------------------------
    def frame_start(self) -> None:
        self.last_frame_start = time.perf_counter()

    def frame_end(self) -> None:
        self._record_interval(self.last_frame_start, self.frame_times)
        self.last_frame_start = None

    def get_fps(self) -> float:
        ft = self.frame_times
        if not ft:
            return 0.0
        try:
            avg = sum(ft) / len(ft)
            return 1.0 / avg if avg > 0 else 0.0
        except Exception:
            return 0.0

    def get_avg_frame_time_ms(self) -> float:
        ft = self.frame_times
        if not ft:
            return 0.0
        try:
            return (sum(ft) / len(ft)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # RENDER TIME
    # ---------------------------------------------------------
    def render_start(self) -> None:
        self.last_render_start = time.perf_counter()

    def render_end(self) -> None:
        self._record_interval(self.last_render_start, self.render_times)
        self.last_render_start = None

    def get_avg_render_time_ms(self) -> float:
        rt = self.render_times
        if not rt:
            return 0.0
        try:
            return (sum(rt) / len(rt)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # MIDI LATENCY
    # ---------------------------------------------------------
    def midi_event_received(self) -> None:
        self.last_midi_event_time = time.perf_counter()

    def midi_event_rendered(self) -> None:
        self._record_interval(self.last_midi_event_time, self.midi_latencies)
        self.last_midi_event_time = None

    def get_avg_midi_latency_ms(self) -> float:
        ml = self.midi_latencies
        if not ml:
            return 0.0
        try:
            return (sum(ml) / len(ml)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # EVENT THROUGHPUT
    # ---------------------------------------------------------
    def event_processed(self) -> None:
        now = time.perf_counter()
        last = self.last_event_time
        if last is not None:
            try:
                dt = now - last
                if dt > 0:
                    self.event_intervals.append(dt)
            except Exception:
                pass
        self.last_event_time = now

    def get_events_per_second(self) -> float:
        ev = self.event_intervals
        if not ev:
            return 0.0
        try:
            avg = sum(ev) / len(ev)
            return 1.0 / avg if avg > 0 else 0.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # PIPELINE METRICS
    # ---------------------------------------------------------
    def record_event_latency(self, pipeline_ms: float) -> None:
        try:
            self.pipeline_latencies.append(float(pipeline_ms))
        except Exception:
            pass

    def record_pipeline_step(self, event_ms: float, ui_ms: float, pipeline_ms: float) -> None:
        try:
            self.event_processing_times.append(float(event_ms))
            self.ui_processing_times.append(float(ui_ms))
            self.pipeline_latencies.append(float(pipeline_ms))
        except Exception:
            pass

    def get_avg_pipeline_latency_ms(self) -> float:
        pl = self.pipeline_latencies
        if not pl:
            return 0.0
        try:
            return sum(pl) / len(pl)
        except Exception:
            return 0.0

    def get_avg_event_processing_ms(self) -> float:
        ep = self.event_processing_times
        if not ep:
            return 0.0
        try:
            return sum(ep) / len(ep)
        except Exception:
            return 0.0

    def get_avg_ui_processing_ms(self) -> float:
        ui = self.ui_processing_times
        if not ui:
            return 0.0
        try:
            return sum(ui) / len(ui)
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # CPU LOAD
    # ---------------------------------------------------------
    def get_cpu_usage_percent(self) -> Optional[float]:
        proc = self.process
        if proc is None:
            return None
        try:
            raw = proc.cpu_percent(interval=0.0)
            if psutil is not None:
                return raw / psutil.cpu_count()
            return raw
        except Exception:
            return None

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    def get_summary(self) -> Dict[str, Any]:
        try:
            return {
                "fps": self.get_fps(),
                "avg_frame_ms": self.get_avg_frame_time_ms(),
                "avg_render_ms": self.get_avg_render_time_ms(),
                "avg_midi_latency_ms": self.get_avg_midi_latency_ms(),
                "avg_pipeline_latency_ms": self.get_avg_pipeline_latency_ms(),
                "avg_event_processing_ms": self.get_avg_event_processing_ms(),
                "avg_ui_processing_ms": self.get_avg_ui_processing_ms(),
                "events_per_second": self.get_events_per_second(),
                "cpu_percent": self.get_cpu_usage_percent(),
            }
        except Exception:
            return {
                "fps": 0.0,
                "avg_frame_ms": 0.0,
                "avg_render_ms": 0.0,
                "avg_midi_latency_ms": 0.0,
                "avg_pipeline_latency_ms": 0.0,
                "avg_event_processing_ms": 0.0,
                "avg_ui_processing_ms": 0.0,
                "events_per_second": 0.0,
                "cpu_percent": None,
            }
