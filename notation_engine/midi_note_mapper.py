from typing import Optional, Dict, Tuple


class Duration:
    def __init__(self, ticks: int, dotted: bool = False):
        self.ticks = int(ticks)
        self.dotted = bool(dotted)

    def __repr__(self):
        return f"Duration(ticks={self.ticks}, dotted={self.dotted})"


class MeasurePosition:
    def __init__(self, measure: int, beat: float):
        self.measure = int(measure)
        self.beat = float(beat)

    def __repr__(self):
        return f"MeasurePosition(measure={self.measure}, beat={self.beat})"


class Note:
    def __init__(
        self,
        pitch: int,
        velocity: int,
        start_time: float,
        duration: Duration,
        channel: int,
        position: MeasurePosition,
    ):
        self.pitch = int(pitch)
        self.velocity = int(velocity)
        self.start_time = float(start_time)
        self.duration = duration
        self.channel = int(channel)
        self.position = position

    def __repr__(self):
        return (
            f"Note(pitch={self.pitch}, velocity={self.velocity}, "
            f"start={self.start_time}, duration={self.duration}, "
            f"channel={self.channel}, position={self.position})"
        )


class MidiNoteMapper:
    """
    Stabilizovaný MIDI → Notation mapper.

    - sleduje aktívne noty (note_on → note_off)
    - konvertuje čas na ticks
    - kvantizuje
    - počíta measure/beat podľa time signature
    - vytvára Note objekt
    """

    def __init__(self, ppq: int = 480, tempo_bpm: float = 120.0):
        self.active_notes: Dict[Tuple[int, int], Dict[str, float]] = {}

        self.ppq = int(ppq)
        self.tempo_bpm = float(tempo_bpm)

        # Position tracking
        self.current_measure = 0
        self.current_beat = 1.0

        # Callback
        self.on_note_created = None

        # Quantization (1/16 note)
        self.quantize_resolution = 120

        # Time signature (default 4/4)
        self.time_numerator = 4
        self.time_denominator = 4

    # ---------------------------------------------------------
    # TIMING
    # ---------------------------------------------------------
    def set_timing(self, ppq: int, tempo_bpm: float):
        try:
            self.ppq = int(ppq)
            self.tempo_bpm = float(tempo_bpm)
        except Exception:
            pass

    def set_time_signature(self, numerator: int, denominator: int):
        try:
            self.time_numerator = int(numerator)
            self.time_denominator = int(denominator)
        except Exception:
            pass

    def _seconds_to_ticks(self, seconds: float) -> int:
        try:
            seconds_per_beat = 60.0 / self.tempo_bpm
            beats = seconds / seconds_per_beat
            return int(round(beats * self.ppq))
        except Exception:
            return 0

    def _quantize_ticks(self, ticks: int) -> int:
        try:
            q = self.quantize_resolution
            return int(round(ticks / q) * q)
        except Exception:
            return ticks

    def _update_position(self, timestamp: float):
        try:
            seconds_per_beat = 60.0 / self.tempo_bpm
            beats = timestamp / seconds_per_beat

            beat_in_measure = (beats % self.time_numerator) + 1
            measure = int(beats // self.time_numerator)

            self.current_measure = measure
            self.current_beat = beat_in_measure
        except Exception:
            self.current_measure = 0
            self.current_beat = 1.0

    # ---------------------------------------------------------
    # MIDI EVENTS
    # ---------------------------------------------------------
    def handle_note_on(self, pitch: int, velocity: int, channel: int, timestamp: float):
        self._update_position(timestamp)

        try:
            self.active_notes[(int(pitch), int(channel))] = {
                "start_time": float(timestamp),
                "velocity": int(velocity),
            }
        except Exception:
            pass

    def handle_note_off(self, pitch: int, channel: int, timestamp: float):
        self._update_position(timestamp)

        key = (int(pitch), int(channel))
        if key not in self.active_notes:
            return

        try:
            start_time = float(self.active_notes[key]["start_time"])
            velocity = int(self.active_notes[key]["velocity"])
        except Exception:
            del self.active_notes[key]
            return

        del self.active_notes[key]

        # Duration
        duration_seconds = max(timestamp - start_time, 0.0)
        duration_ticks = self._seconds_to_ticks(duration_seconds)
        duration_ticks = self._quantize_ticks(duration_ticks)
        duration = Duration(ticks=duration_ticks)

        # Quantized beat
        try:
            quantized_beat = round(self.current_beat * 4) / 4
        except Exception:
            quantized_beat = 1.0

        position = MeasurePosition(
            measure=self.current_measure,
            beat=quantized_beat,
        )

        note = Note(
            pitch=pitch,
            velocity=velocity,
            start_time=start_time,
            duration=duration,
            channel=channel,
            position=position,
        )

        # Callback
        if callable(self.on_note_created):
            try:
                self.on_note_created(note)
            except Exception:
                pass
