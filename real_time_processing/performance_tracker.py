import time
import collections

try:
    import psutil
except ImportError:
    psutil = None


class PerformanceTracker:
    """
    Real‑time performance tracker for the entire pipeline.

    Stabilizované:
    - ochrana pred None
    - bezpečné výpočty FPS, render time, MIDI latency
    - fallback pri chybách
    - CPU usage cez psutil (ak je dostupný)
    """

    def __init__(self, history_size=300):
        try:
            history_size = int(history_size)
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

        # PIPELINE METRIKY
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
    # FRAME / FPS
    # ---------------------------------------------------------

    def frame_start(self):
        self.last_frame_start = time.time()

    def frame_end(self):
        if self.last_frame_start is None:
            return
        try:
            dt = time.time() - self.last_frame_start
            self.frame_times.append(dt)
        except Exception:
            pass
        self.last_frame_start = None

    def get_fps(self):
        if not self.frame_times:
            return 0.0
        try:
            avg = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg if avg > 0 else 0.0
        except Exception:
            return 0.0

    def get_avg_frame_time_ms(self):
        if not self.frame_times:
            return 0.0
        try:
            return (sum(self.frame_times) / len(self.frame_times)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # RENDER TIME
    # ---------------------------------------------------------

    def render_start(self):
        self.last_render_start = time.time()

    def render_end(self):
        if self.last_render_start is None:
            return
        try:
            dt = time.time() - self.last_render_start
            self.render_times.append(dt)
        except Exception:
            pass
        self.last_render_start = None

    def get_avg_render_time_ms(self):
        if not self.render_times:
            return 0.0
        try:
            return (sum(self.render_times) / len(self.render_times)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # MIDI LATENCY
    # ---------------------------------------------------------

    def midi_event_received(self):
        self.last_midi_event_time = time.time()

    def midi_event_rendered(self):
        if self.last_midi_event_time is None:
            return
        try:
            dt = time.time() - self.last_midi_event_time
            self.midi_latencies.append(dt)
        except Exception:
            pass
        self.last_midi_event_time = None

    def get_avg_midi_latency_ms(self):
        if not self.midi_latencies:
            return 0.0
        try:
            return (sum(self.midi_latencies) / len(self.midi_latencies)) * 1000.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # EVENT THROUGHPUT
    # ---------------------------------------------------------

    def event_processed(self):
        now = time.time()
        try:
            if self.last_event_time is not None:
                dt = now - self.last_event_time
                if dt > 0:
                    self.event_intervals.append(dt)
        except Exception:
            pass
        self.last_event_time = now

    def get_events_per_second(self):
        if not self.event_intervals:
            return 0.0
        try:
            avg = sum(self.event_intervals) / len(self.event_intervals)
            return 1.0 / avg if avg > 0 else 0.0
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # PIPELINE METRIKY
    # ---------------------------------------------------------

    def record_event_latency(self, pipeline_ms):
        try:
            self.pipeline_latencies.append(float(pipeline_ms))
        except Exception:
            pass

    def record_pipeline_step(self, event_ms, ui_ms, pipeline_ms):
        try:
            self.event_processing_times.append(float(event_ms))
            self.ui_processing_times.append(float(ui_ms))
            self.pipeline_latencies.append(float(pipeline_ms))
        except Exception:
            pass

    def get_avg_pipeline_latency_ms(self):
        if not self.pipeline_latencies:
            return 0.0
        try:
            return sum(self.pipeline_latencies) / len(self.pipeline_latencies)
        except Exception:
            return 0.0

    def get_avg_event_processing_ms(self):
        if not self.event_processing_times:
            return 0.0
        try:
            return sum(self.event_processing_times) / len(self.event_processing_times)
        except Exception:
            return 0.0

    def get_avg_ui_processing_ms(self):
        if not self.ui_processing_times:
            return 0.0
        try:
            return sum(self.ui_processing_times) / len(self.ui_processing_times)
        except Exception:
            return 0.0

    # ---------------------------------------------------------
    # CPU LOAD
    # ---------------------------------------------------------

    def get_cpu_usage_percent(self):
        if self.process is None:
            return None
        try:
            return self.process.cpu_percent(interval=0.0)
        except Exception:
            return None

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    def get_summary(self):
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
