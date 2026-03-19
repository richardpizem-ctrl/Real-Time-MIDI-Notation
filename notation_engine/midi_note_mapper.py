class Duration:
    def __init__(self, ticks: int, dotted: bool = False):
        self.ticks = ticks
        self.dotted = dotted

    def __repr__(self):
        return f"Duration(ticks={self.ticks}, dotted={self.dotted})"


class MeasurePosition:
    def __init__(self, measure: int, beat: float):
        self.measure = measure
        self.beat = beat  # napr. 1.0, 1.5, 2.0, 2.75

    def __repr__(self):
        return f"MeasurePosition(measure={self.measure}, beat={self.beat})"


class Note:
    def __init__(self, pitch: int, velocity: int, start_time: float,
                 duration: Duration, channel: int,
                 position: MeasurePosition):
        self.pitch = pitch
        self.velocity = velocity
        self.start_time = start_time
        self.duration = duration
        self.channel = channel
        self.position = position

    def __repr__(self):
        return (
            f"Note(pitch={self.pitch}, velocity={self.velocity}, "
            f"start={self.start_time}, duration={self.duration}, "
            f"channel={self.channel}, position={self.position})"
        )


class MidiNoteMapper:
    def __init__(self, ppq: int = 480, tempo_bpm: float = 120.0):
        self.active_notes = {}  # (pitch, channel) -> {start_time, velocity}
        self.ppq = ppq
        self.tempo_bpm = tempo_bpm
        self.current_measure = 0
        self.current_beat = 1.0
        self.on_note_created = None  # callback: fn(note: Note) -> None

    def set_timing(self, ppq: int, tempo_bpm: float):
        self.ppq = ppq
        self.tempo_bpm = tempo_bpm

    def _seconds_to_ticks(self, seconds: float) -> int:
        # 1 beat = 60 / BPM sekúnd
        seconds_per_beat = 60.0 / self.tempo_bpm
        beats = seconds / seconds_per_beat
        return int(round(beats * self.ppq))

    def handle_note_on(self, pitch: int, velocity: int,
                       channel: int, timestamp: float):
        self.active_notes[(pitch, channel)] = {
            "start_time": timestamp,
            "velocity": velocity,
        }

    def handle_note_off(self, pitch: int, channel: int, timestamp: float):
        key = (pitch, channel)
        if key not in self.active_notes:
            return

        start_time = self.active_notes[key]["start_time"]
        velocity = self.active_notes[key]["velocity"]
        del self.active_notes[key]

        duration_seconds = timestamp - start_time
        duration_ticks = self._seconds_to_ticks(duration_seconds)
        duration = Duration(ticks=duration_ticks)

        position = MeasurePosition(
            measure=self.current_measure,
            beat=self.current_beat
        )

        note = Note(
            pitch=pitch,
            velocity=velocity,
            start_time=start_time,
            duration=duration,
            channel=channel,
            position=position
        )

        if self.on_note_created is not None:
            self.on_note_created(note)
