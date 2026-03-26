import time
import collections

try:
    import psutil
except ImportError:
    psutil = None


class PerformanceTracker:
    def __init__(self, history_size=300):
        # FRAME TIME (FPS)
        self.frame_times = collections.deque(maxlen=history_size)
        self.last_frame_start = None

        # RENDER TIME
        self.render_times = collections.deque(maxlen=history_size)
        self.last_render_start = None

        # MIDI LATENCY (pôvodné)
        self.midi_latencies = collections.deque(maxlen=history_size)
        self.last_midi_event_time = None

        # EVENT THROUGHPUT
        self.event_intervals = collections.deque(maxlen=history_size)
        self.last_event_time = None

        # PIPELINE METRIKY (NOVÉ)
        self.event_processing_times = collections.deque(maxlen=history_size)
        self.ui_processing_times = collections.deque(maxlen=history_size)
        self.pipeline_latencies = collections.deque(maxlen=history_size)

        # CPU
        if psutil is not None:
            self.process = psutil.Process()
        else:
            self.process = None

    # ---------------- FRAME / FPS ----------------

    def frame_start(self):
        self.last_frame_start = time.time()

    def frame_end(self):
        if self.last_frame_start is None:
            return
        dt = time.time() - self.last_frame_start
        self.frame_times.append(dt)
        self.last_frame_start = None

    def get_fps(self):
        if not self.frame_times:
            return 0.0
        avg = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg if avg > 0 else 0.0

    def get_avg_frame_time_ms(self):
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000.0

    # ---------------- RENDER TIME ----------------

    def render_start(self):
        self.last_render_start = time.time()

    def render_end(self):
        if self.last_render_start is None:
            return
        dt = time.time() - self.last_render_start
        self.render_times.append(dt)
        self.last_render_start = None

    def get_avg_render_time_ms(self):
        if not self.render_times:
            return 0.0
        return (sum(self.render_times) / len(self.render_times)) * 1000.0

    # ---------------- MIDI LATENCY ----------------

    def midi_event_received(self):
        self.last_midi_event_time = time.time()

    def midi_event_rendered(self):
        if self.last_midi_event_time is None:
            return
        dt = time.time() - self.last_midi_event_time
        self.midi_latencies.append(dt)
        self.last_midi_event_time = None

    def get_avg_midi_latency_ms(self):
        if not self.midi_latencies:
            return 0.0
        return (sum(self.midi_latencies) / len(self.midi_latencies)) * 1000.0

    # ---------------- EVENT THROUGHPUT ----------------

    def event_processed(self):
        now = time.time()
        if self.last_event_time is not None:
            dt = now - self.last_event_time
            if dt > 0:
                self.event_intervals.append(dt)
        self.last_event_time = now

    def get_events_per_second(self):
        if not self.event_intervals:
            return 0.0
        avg = sum(self.event_intervals) / len(self.event_intervals)
        return 1.0 / avg if avg > 0 else 0.0

    # ---------------- PIPELINE METRIKY (NOVÉ) ----------------

    def record_event_latency(self, pipeline_ms):
        """Celková latencia jedného MIDI eventu."""
        self.pipeline_latencies.append(pipeline_ms)

    def record_pipeline_step(self, event_ms, ui_ms, pipeline_ms):
        """Detailné metriky pre debug overlay."""
        self.event_processing_times.append(event_ms)
        self.ui_processing_times.append(ui_ms)
        self.pipeline_latencies.append(pipeline_ms)

    def get_avg_pipeline_latency_ms(self):
        if not self.pipeline_latencies:
            return 0.0
        return sum(self.pipeline_latencies) / len(self.pipeline_latencies)

    def get_avg_event_processing_ms(self):
        if not self.event_processing_times:
            return 0.0
        return sum(self.event_processing_times) / len(self.event_processing_times)

    def get_avg_ui_processing_ms(self):
        if not self.ui_processing_times:
            return 0.0
        return sum(self.ui_processing_times) / len(self.ui_processing_times)

    # ---------------- CPU LOAD ----------------

    def get_cpu_usage_percent(self):
        if self.process is None:
            return None
        return self.process.cpu_percent(interval=0.0)

    # ---------------- SUMMARY ----------------

    def get_summary(self):
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
