# =========================================================
# MidiNoteMapper v4.3.0
# Stabilizovaný MIDI → Notation mapper pre Real-Time-MIDI-Notation
# =========================================================

from typing import Optional, Dict, Tuple, Callable


class Duration:
    __slots__ = ("ticks", "dotted")

    def __init__(self, ticks: int, dotted: bool = False):
        try:
            self.ticks = int(ticks)
        except Exception:
            self.ticks = 0
        self.dotted = bool(dotted)

    def __repr__(self) -> str:
        return f"Duration(ticks={self.ticks}, dotted={self.dotted})"


class MeasurePosition:
    __slots__ = ("measure", "beat")

    def __init__(self, measure: int, beat: float):
        try:
            self.measure = int(measure)
        except Exception:
            self.measure = 0
        try:
            self.beat = float(beat)
        except Exception:
            self.beat = 1.0

    def __repr__(self) -> str:
        return f"MeasurePosition(measure={self.measure}, beat={self.beat})"


class Note:
    __slots__ = (
        "pitch",
        "velocity",
        "start_time",
        "duration",
        "channel",
        "position",
    )

    def __init__(
        self,
        pitch: int,
        velocity: int,
        start_time: float,
        duration: Duration,
        channel: int,
        position: MeasurePosition,
    ):
        try:
            self.pitch = int(pitch)
        except Exception:
            self.pitch = 60

        try:
            self.velocity = int(velocity)
        except Exception:
            self.velocity = 100

        try:
            self.start_time = float(start_time)
        except Exception:
            self.start_time = 0.0

        self.duration = duration if isinstance(duration, Duration) else Duration(0)

        try:
            self.channel = int(channel)
        except Exception:
            self.channel = 0

        self.position = (
            position
            if isinstance(position, MeasurePosition)
            else MeasurePosition(0, 1.0)
        )

    def __repr__(self) -> str:
        return (
            f"Note(pitch={self.pitch}, velocity={self.velocity}, "
            f"start={self.start_time}, duration={self.duration}, "
            f"channel={self.channel}, position={self.position})"
        )


class MidiNoteMapper:
    """
    MidiNoteMapper (v4.3.0) – stabilizovaný MIDI → Notation mapper.

    - sleduje aktívne noty (note_on → note_off)
    - konvertuje čas na ticks
    - kvantizuje
    - počíta measure/beat podľa time signature
    - vytvára Note objekt
    - real-time safe, deterministické
    """

    __slots__ = (
        "active_notes",
        "ppq",
        "tempo_bpm",
        "current_measure",
        "current_beat",
        "on_note_created",
        "quantize_resolution",
        "time_numerator",
        "time_denominator",
    )

    def __init__(self, ppq: int = 480, tempo_bpm: float = 120.0):
        self.active_notes: Dict[Tuple[int, int], Dict[str, float]] = {}

        try:
            self.ppq = int(ppq)
        except Exception:
            self.ppq = 480

        try:
            self.tempo_bpm = float(tempo_bpm)
        except Exception:
            self.tempo_bpm = 120.0

        self.current_measure: int = 0
        self.current_beat: float = 1.0

        self.on_note_created: Optional[Callable[[Note], None]] = None

        self.quantize_resolution: int = 120

        self.time_numerator: int = 4
        self.time_denominator: int = 4

    # ---------------------------------------------------------
    # TIMING
    # ---------------------------------------------------------
    def set_timing(self, ppq: int, tempo_bpm: float) -> None:
        try:
            self.ppq = int(ppq)
        except Exception:
            pass
        try:
            self.tempo_bpm = float(tempo_bpm)
        except Exception:
            pass

    def set_time_signature(self, numerator: int, denominator: int) -> None:
        try:
            self.time_numerator = int(numerator)
        except Exception:
            pass
        try:
            self.time_denominator = int(denominator)
        except Exception:
            pass

    def _seconds_to_ticks(self, seconds: float) -> int:
        try:
            seconds = float(seconds)
        except Exception:
            return 0

        try:
            seconds_per_beat = 60.0 / self.tempo_bpm
            beats = seconds / seconds_per_beat
            return int(round(beats * self.ppq))
        except Exception:
            return 0

    def _quantize_ticks(self, ticks: int) -> int:
        try:
            ticks = int(ticks)
        except Exception:
            return 0

        try:
            q = int(self.quantize_resolution)
            if q <= 0:
                return ticks
            return int(round(ticks / q) * q)
        except Exception:
            return ticks

    def _update_position(self, timestamp: float) -> None:
        try:
            timestamp = float(timestamp)
        except Exception:
            self.current_measure = 0
            self.current_beat = 1.0
            return

        try:
            seconds_per_beat = 60.0 / self.tempo_bpm
            beats = timestamp / seconds_per_beat

            if self.time_numerator <= 0:
                self.time_numerator = 4

            beat_in_measure = (beats % self.time_numerator) + 1
            measure = int(beats // self.time_numerator)

            self.current_measure = max(0, measure)
            self.current_beat = max(1.0, float(beat_in_measure))
        except Exception:
            self.current_measure = 0
            self.current_beat = 1.0

    # ---------------------------------------------------------
    # MIDI EVENTS
    # ---------------------------------------------------------
    def handle_note_on(self, pitch: int, velocity: int, channel: int, timestamp: float) -> None:
        self._update_position(timestamp)

        try:
            key = (int(pitch), int(channel))
        except Exception:
            return

        try:
            self.active_notes[key] = {
                "start_time": float(timestamp),
                "velocity": int(velocity),
            }
        except Exception:
            pass

    def handle_note_off(self, pitch: int, channel: int, timestamp: float) -> None:
        self._update_position(timestamp)

        try:
            key = (int(pitch), int(channel))
        except Exception:
            return

        if key not in self.active_notes:
            return

        try:
            start_time = float(self.active_notes[key]["start_time"])
            velocity = int(self.active_notes[key]["velocity"])
        except Exception:
            del self.active_notes[key]
            return

        del self.active_notes[key]

        try:
            duration_seconds = max(float(timestamp) - start_time, 0.0)
        except Exception:
            duration_seconds = 0.0

        duration_ticks = self._seconds_to_ticks(duration_seconds)
        duration_ticks = self._quantize_ticks(duration_ticks)
        duration = Duration(ticks=duration_ticks)

        try:
            quantized_beat = round(self.current_beat * 4) / 4
        except Exception:
            quantized_beat = 1.0

        position = MeasurePosition(
            measure=self.current_measure,
            beat=quantized_beat,
        )

        note = Note(
            pitch=key[0],
            velocity=velocity,
            start_time=start_time,
            duration=duration,
            channel=key[1],
            position=position,
        )

        callback = self.on_note_created
        if callable(callback):
            try:
                callback(note)
            except Exception:
                pass
