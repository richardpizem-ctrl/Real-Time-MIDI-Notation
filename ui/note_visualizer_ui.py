# =========================================================
# NoteVisualizerUI v2.0.0
# Stabilný real‑time MIDI vizualizér s BPM pulzom
# =========================================================

import pygame
import time
from typing import Dict, Tuple, Any


class NoteVisualizerUI:
    """
    Real‑time vizualizér MIDI nôt s farebným pulzovaním.
    Každá nota vytvorí pulz, ktorý postupne mizne.
    Obsahuje aj BPM pulz pre globálny rytmický efekt.
    """

    def __init__(self, width: int = 1400, height: int = 200) -> None:
        self.width = int(width)
        self.height = int(height)

        # Aktívne pulzy: midi -> {color, timestamp}
        self.active_notes: Dict[int, Dict[str, Any]] = {}

        # BPM pulz
        self.bpm: int = 120
        self.last_pulse_time: float = time.time()

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

    # ---------------------------------------------------------
    # PUBLIC API (UIManager-safe)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str) -> None:
        return

    def update_visibility(self, track_index: int, visible: bool) -> None:
        return

    def set_active_track(self, track_index: int) -> None:
        return

    # ---------------------------------------------------------
    # BPM PULSE
    # ---------------------------------------------------------
    def update_bpm_pulse(self, bpm: float, timestamp: float) -> None:
        """Aktualizuje BPM pulz (volané z UIManager)."""
        try:
            self.bpm = max(1, int(bpm))
        except Exception:
            self.bpm = 120

        try:
            self.last_pulse_time = float(timestamp)
        except Exception:
            self.last_pulse_time = time.time()

    # ---------------------------------------------------------
    # NOTE EVENTS
    # ---------------------------------------------------------
    def on_note(self, event: Dict[str, Any]) -> None:
        """
        event:
            note: int
            track_color: (r,g,b)
            time: float
        """
        midi = event.get("note")
        if midi is None:
            return

        try:
            midi_int = int(midi)
        except Exception:
            return

        color = event.get("track_color", (255, 80, 80))
        if not isinstance(color, (tuple, list)) or len(color) != 3:
            color = (255, 80, 80)

        self.active_notes[midi_int] = {
            "color": tuple(color),
            "timestamp": time.time(),
        }

    def on_note_off(self, event: Dict[str, Any]) -> None:
        midi = event.get("note")
        try:
            midi_int = int(midi)
        except Exception:
            return

        if midi_int in self.active_notes:
            del self.active_notes[midi_int]

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if surface is None:
            return

        surface.fill((20, 20, 20))
        now = time.time()

        # BPM pulz
        beat_interval = 60.0 / max(1, self.bpm)
        beat_phase = (now - self.last_pulse_time) / beat_interval
        beat_strength = max(0.0, 1.0 - beat_phase)

        # Globálne pozadie pulzu
        bg_intensity = int(beat_strength * 40)
        pygame.draw.rect(
            surface,
            (bg_intensity, bg_intensity, bg_intensity),
            (0, 0, self.width, self.height),
        )

        # NOTE PULZY
        for midi in list(self.active_notes):
            data = self.active_notes.get(midi)
            if not data:
                continue

            color: Tuple[int, int, int] = data.get("color", (255, 80, 80))
            t: float = data.get("timestamp", now)

            fade = max(0.0, 1.0 - (now - t) * 1.2)

            if fade <= 0.0:
                del self.active_notes[midi]
                continue

            # Pozícia podľa MIDI výšky
            y = int(self.height - (midi - 36) * 2.2)
            y = max(0, min(self.height, y))

            x = int((midi * 37) % self.width)

            radius = int(20 + fade * 40)

            pulsed_color = (
                int(color[0] * fade),
                int(color[1] * fade),
                int(color[2] * fade),
            )

            pygame.draw.circle(surface, pulsed_color, (x, y), radius)

        # Oddelovacia čiara
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (0, self.height - 2),
            (self.width, self.height - 2),
            2,
        )
