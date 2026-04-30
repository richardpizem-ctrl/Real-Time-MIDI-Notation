"""
note_visualizer_ui.py – Real‑Time Note Visualizer (FÁZA 4)

Jednoduchý real‑time vizualizér MIDI nôt s farebným pulzovaním.
Každá nota vytvorí pulz, ktorý postupne mizne. Modul obsahuje aj
globálny BPM pulz pre vizuálny rytmus.

Poskytuje:
- farebné pulzy pre každú aktívnu notu
- BPM pulz (globálne blikanie podľa tempa)
- fade-out efekt pre noty
- bezpečné no-op metódy pre UIManager
- kompatibilitu s real‑time MIDI pipeline

Prepojenia:
- používa sa ako doplnková UI vrstva (midi_input → engine → UIManager → NoteVisualizerUI)
- prijíma eventy vo formáte: {note, track_color, time}
- funguje paralelne s PianoUI a GraphicNotationRenderer
"""

import pygame
import time
from typing import Dict, Tuple, Any


class NoteVisualizerUI:
    """
    Jednoduchý vizualizér MIDI nôt s pulzovaním podľa BPM.
    Každá nota vytvorí farebný pulz, ktorý postupne mizne.
    """

    def __init__(self, width: int = 1400, height: int = 200) -> None:
        self.width = int(width)
        self.height = int(height)

        # aktívne pulzy: midi -> {color, timestamp}
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
    # PUBLIC API (pre UIManager – bezpečné no-op metódy)
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

        # timestamp očakávame v sekundách (float)
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
            note
            track_color
            time
        """
        midi = event.get("note")
        if midi is None:
            return

        try:
            midi_int = int(midi)
        except Exception:
            return

        color = event.get("track_color", (255, 80, 80))
        if (
            not isinstance(color, (tuple, list))
            or len(color) != 3
        ):
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

        # BPM pulz (globálny)
        beat_interval = 60.0 / max(1, self.bpm)
        beat_phase = (now - self.last_pulse_time) / beat_interval
        beat_strength = max(0.0, 1.0 - beat_phase)

        # pozadie pulzu
        bg_intensity = int(beat_strength * 40)
        pygame.draw.rect(
            surface,
            (bg_intensity, bg_intensity, bg_intensity),
            (0, 0, self.width, self.height),
        )

        # NOTE PULZY
        # iterujeme cez kľúče, aby mazanie bolo lacnejšie
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

            # pozícia podľa MIDI výšky
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

        # oddelovacia čiara
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (0, self.height - 2),
            (self.width, self.height - 2),
            2,
        )
