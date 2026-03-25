import time
import collections

try:
    import psutil
except ImportError:
    psutil = None


class PerformanceTracker:
    def __init__(self, history_size=300):
        # čas trvania frame-ov (celý frame)
        self.frame_times = collections.deque(maxlen=history_size)
        self.last_frame_start = None

        # čas trvania renderu
        self.render_times = collections.deque(maxlen=history_size)
        self.last_render_start = None

        # MIDI latencia: čas medzi prijatím MIDI eventu a jeho zobrazením / spracovaním
        self.midi_latencies = collections.deque(maxlen=history_size)
        self.last_midi_event_time = None

        # throughput eventov (koľko eventov za sekundu)
        self.event_intervals = collections.deque(maxlen=history_size)
        self.last_event_time = None

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
        if avg <= 0:
            return 0.0
        return 1.0 / avg

    def get_avg_frame_time_ms(self):
        if not self.frame_times:
            return 0.0
        avg = sum(self.frame_times) / len(self.frame_times)
        return avg * 1000.0

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
        avg = sum(self.render_times) / len(self.render_times)
        return avg * 1000.0

    # ---------------- MIDI LATENCY ----------------

    def midi_event_received(self):
        """Zavolaj pri prijatí MIDI eventu (napr. NOTE_ON)."""
        self.last_midi_event_time = time.time()

    def midi_event_rendered(self):
        """Zavolaj, keď sa daný MIDI event prejaví v UI / zvuku."""
        if self.last_midi_event_time is None:
            return
        dt = time.time() - self.last_midi_event_time
        self.midi_latencies.append(dt)
        self.last_midi_event_time = None

    def get_avg_midi_latency_ms(self):
        if not self.midi_latencies:
            return 0.0
        avg = sum(self.midi_latencies) / len(self.midi_latencies)
        return avg * 1000.0

    # ---------------- EVENT THROUGHPUT ----------------

    def event_processed(self):
        """Zavolaj pri každom spracovanom evente (MIDI, UI, atď.)."""
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
        if avg <= 0:
            return 0.0
        return 1.0 / avg

    # ---------------- CPU LOAD ----------------

    def get_cpu_usage_percent(self):
        """
        Vráti CPU usage procesu v %, alebo None, ak psutil nie je dostupný.
        """
        if self.process is None:
            return None
        # krátke intervalové meranie
        return self.process.cpu_percent(interval=0.0)

    # ---------------- SUMMARY ----------------

    def get_summary(self):
        """
        Vráti dict so všetkými metrikami naraz.
        """
        return {
            "fps": self.get_fps(),
            "avg_frame_ms": self.get_avg_frame_time_ms(),
            "avg_render_ms": self.get_avg_render_time_ms(),
            "avg_midi_latency_ms": self.get_avg_midi_latency_ms(),
            "events_per_second": self.get_events_per_second(),
            "cpu_percent": self.get_cpu_usage_percent(),
        }
