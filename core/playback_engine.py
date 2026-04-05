"""
PlaybackEngine – realtime prehrávací modul pre Real-Time-MIDI-Notation.

- riadi čas a prehrávanie
- synchronizuje GraphicNotationRenderer a CanvasUI
- používa TrackManager na DAW-logiku (mute/solo/volume)
"""

import time
from typing import List, Dict, Any, Optional

from core.track_manager import TrackManager
from renderer.graphic_renderer import GraphicNotationRenderer
from ui.canvas_ui import CanvasUI
from core.logger import Logger


class PlaybackEngine:
    def __init__(
        self,
        track_manager: TrackManager,
        renderer: GraphicNotationRenderer,
        canvas_ui: CanvasUI,
        bpm: float = 120.0,
        beats_per_bar: int = 4,
    ):
        self.track_manager = track_manager
        self.renderer = renderer
        self.canvas_ui = canvas_ui

        # Tempo / meter
        self.bpm: float = bpm
        self.beats_per_bar: int = beats_per_bar

        # Playback state
        self.playing: bool = False
        self.position_sec: float = 0.0
        self._last_time: float = time.time()

        # Timeline notes
        self.notes: List[Dict[str, Any]] = []

        self._sync_renderer_tempo()
        Logger.info("PlaybackEngine initialized.")

    # ---------------------------------------------------------
    # INTERNAL: TEMPO SYNC
    # ---------------------------------------------------------
    def _sync_renderer_tempo(self):
        """Synchronizuje BPM a meter do rendereru."""
        if self.renderer is None:
            return

        try:
            self.renderer.bpm = float(self.bpm)
        except Exception:
            Logger.warning("Renderer rejected BPM value.")

        try:
            self.renderer.beats_per_bar = int(self.beats_per_bar)
        except Exception:
            Logger.warning("Renderer rejected beats_per_bar value.")

    # ---------------------------------------------------------
    # TEMPO / METER API
    # ---------------------------------------------------------
    def set_bpm(self, bpm: float):
        try:
            bpm = float(bpm)
        except Exception:
            return

        if bpm <= 0:
            return

        self.bpm = bpm
        self._sync_renderer_tempo()

    def set_beats_per_bar(self, beats: int):
        try:
            beats = int(beats)
        except Exception:
            return

        if beats < 1:
            return

        self.beats_per_bar = beats
        self._sync_renderer_tempo()

    # ---------------------------------------------------------
    # NOTES TIMELINE
    # ---------------------------------------------------------
    def set_notes(self, notes: List[Dict[str, Any]]):
        """Nastaví kompletný zoznam nôt pre prehrávanie."""
        if not isinstance(notes, (list, tuple)):
            self.notes = []
            return

        cleaned: List[Dict[str, Any]] = []
        for n in notes:
            if isinstance(n, dict):
                cleaned.append(dict(n))

        cleaned.sort(key=lambda n: float(n.get("timestamp", 0.0)))
        self.notes = cleaned

    # ---------------------------------------------------------
    # PLAYBACK CONTROL
    # ---------------------------------------------------------
    def play(self):
        self.playing = True
        self._last_time = time.time()
        Logger.info("Playback started.")

    def pause(self):
        self.playing = False
        Logger.info("Playback paused.")

    def stop(self):
        self.playing = False
        self.position_sec = 0.0
        Logger.info("Playback stopped.")

    def seek(self, position_sec: float):
        try:
            position_sec = float(position_sec)
        except Exception:
            return

        if position_sec < 0:
            position_sec = 0.0

        self.position_sec = position_sec

    def is_playing(self) -> bool:
        return self.playing

    # ---------------------------------------------------------
    # INTERNAL: TIME UPDATE
    # ---------------------------------------------------------
    def _update_time(self):
        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        if dt < 0:
            dt = 0.0

        if self.playing:
            self.position_sec += dt
            if self.position_sec < 0:
                self.position_sec = 0.0

    # ---------------------------------------------------------
    # ACTIVE NOTES SELECTION
    # ---------------------------------------------------------
    def _collect_active_notes(self) -> List[Dict[str, Any]]:
        """Vyberie noty, ktoré sú aktívne v čase self.position_sec."""
        active: List[Dict[str, Any]] = []
        t_now = self.position_sec

        for note in self.notes:
            try:
                start = float(note.get("timestamp", 0.0))
            except Exception:
                start = 0.0

            try:
                duration = float(note.get("duration", 0.0))
            except Exception:
                duration = 0.0

            if duration <= 0:
                duration = 0.05

            end = start + duration

            if not (start <= t_now <= end):
                continue

            track_id = note.get("track_id")
            if track_id is None:
                continue

            pitch = note.get("pitch", note.get("note"))
            velocity = note.get("velocity", 100)

            if pitch is None:
                continue

            try:
                pitch_int = int(pitch)
                vel_int = int(velocity)
            except Exception:
                continue

            if self.track_manager:
                transformed = self.track_manager.apply_midi_transform(track_id, pitch_int, vel_int)
                if transformed is None:
                    continue
                new_pitch, new_vel = transformed
            else:
                new_pitch, new_vel = pitch_int, vel_int

            active.append(
                {
                    "timestamp": start,
                    "track_id": track_id,
                    "pitch": new_pitch,
                    "velocity": new_vel,
                }
            )

        return active

    # ---------------------------------------------------------
    # MAIN UPDATE LOOP
    # ---------------------------------------------------------
    def update(self) -> Optional[Any]:
        """
        Hlavný tick:
        - aktualizuje čas
        - vyberie aktívne noty
        - zavolá renderer.draw(active_notes)
        - posunie playhead v CanvasUI
        """
        self._update_time()

        # Sync playhead do CanvasUI
        if self.canvas_ui:
            try:
                self.canvas_ui.set_playhead_time(int(self.position_sec * 1000))
            except Exception:
                Logger.warning("CanvasUI rejected playhead update.")

        # Aktívne noty
        active_notes = self._collect_active_notes()

        # Renderer
        surface = None
        if self.renderer:
            try:
                surface = self.renderer.draw(active_notes)
            except Exception as e:
                Logger.error(f"Renderer error: {e}")

        return surface
