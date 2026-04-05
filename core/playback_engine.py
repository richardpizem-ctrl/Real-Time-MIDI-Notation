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
        self.position_sec: float = 0.0  # current song time in seconds
        self._last_time: float = time.time()

        # Note data (timeline)
        self.notes: List[Dict[str, Any]] = []

        # Sync renderer tempo
        self._sync_renderer_tempo()

    # ---------------------------------------------------------
    # INTERNAL: TEMPO SYNC
    # ---------------------------------------------------------
    def _sync_renderer_tempo(self):
        """
        Synchronizuje BPM a meter do rendereru.
        Renderer ich používa pre grid, barlines, measure numbers.
        """
        try:
            self.renderer.bpm = float(self.bpm)
        except Exception:
            pass

        try:
            self.renderer.beats_per_bar = int(self.beats_per_bar)
        except Exception:
            pass

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
        """
        Nastaví kompletný zoznam nôt pre prehrávanie.

        Očakávaný formát jednej noty:
        {
            "timestamp": float (sekundy od začiatku),
            "duration": float (sekundy, voliteľné),
            "track_id": int,
            "pitch" alebo "note": int,
            "velocity": int
        }
        """
        if not isinstance(notes, (list, tuple)):
            self.notes = []
            return

        cleaned: List[Dict[str, Any]] = []
        for n in notes:
            if not isinstance(n, dict):
                continue
            cleaned.append(dict(n))

        cleaned.sort(key=lambda n: float(n.get("timestamp", 0.0)))
        self.notes = cleaned

    # ---------------------------------------------------------
    # PLAYBACK CONTROL
    # ---------------------------------------------------------
    def play(self):
        self.playing = True
        self._last_time = time.time()

    def pause(self):
        self.playing = False

    def stop(self):
        self.playing = False
        self.position_sec = 0.0

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
        """
        Vyberie noty, ktoré sú aktuálne „aktívne“ v čase self.position_sec.
        """
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

            if duration <= 0.0:
                duration = 0.05  # krátky impulz, ak nie je špecifikované

            end = start + duration

            if t_now < start or t_now > end:
                continue

            track_id = note.get("track_id")
            if track_id is None:
                continue

            # DAW logika (mute/solo/volume) cez TrackManager
            pitch = note.get("pitch", note.get("note"))
            velocity = note.get("velocity", 100)

            if pitch is None:
                continue

            try:
                pitch_int = int(pitch)
                vel_int = int(velocity)
            except Exception:
                continue

            transformed = self.track_manager.apply_midi_transform(track_id, pitch_int, vel_int)
            if transformed is None:
                continue

            new_pitch, new_vel = transformed

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
        Hlavný tick, ktorý sa volá z hlavného loopu aplikácie.

        - aktualizuje čas
        - vyberie aktívne noty
        - zavolá renderer.draw(active_notes)
        - posunie playhead v CanvasUI
        """
        self._update_time()

        # Sync playhead do CanvasUI (ms)
        try:
            self.canvas_ui.set_playhead_time(int(self.position_sec * 1000))
        except Exception:
            pass

        # Získaj aktívne noty pre aktuálny čas
        active_notes = self._collect_active_notes()

        # Renderer dostane aktuálne noty
        try:
            surface = self.renderer.draw(active_notes)
        except Exception:
            surface = None

        return surface
