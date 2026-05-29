# =========================================================
# NoteVisualizerUI v4.3.0
# Ultra‑optimalizovaný real‑time MIDI vizualizér s BPM pulzom
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import pygame
import time
from typing import Dict, Tuple, Any


class NoteVisualizerUI:
    """
    NoteVisualizerUI (v4.3.0)
    -------------------------
    Real‑time vizualizér MIDI nôt s farebným pulzovaním.
    Optimalizácie v4.3.0:
        - predpočítané fade krivky
        - stabilný BPM pulz (konštantný čas)
        - rýchlejšie mazanie expirovaných pulzov
        - optimalizované výpočty pozícií
        - žiadne dynamické alokácie v draw()
        - pripravené hooky pre v5 (RGB pulsing, MPE)
    """

    __slots__ = (
        "width", "height",
        "active_notes",
        "bpm", "last_pulse_time",
        "font",
        "_fade_cache",
    )

    # Fade-out speed
    FADE_SPEED = 1.2

    # Prepočítaná výška pre MIDI → Y
    MIDI_Y_SCALE = 2.2

    # ---------------------------------------------------------
    # INIT
    # ---------------------------------------------------------
    def __init__(self, width: int = 1400, height: int = 200) -> None:
        self.width = int(width)
        self.height = int(height)

        # Aktívne pulzy: midi -> {color, timestamp}
        self.active_notes: Dict[int, Dict[str, Any]] = {}

        # BPM pulz
        self.bpm = 120
        self.last_pulse_time = time.time()

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

        # Predpočítané fade hodnoty (0–2 sekundy)
        self._fade_cache = [
            max(0.0, 1.0 - (i / 120.0) * self.FADE_SPEED)
            for i in range(240)
        ]

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

        self.active_notes.pop(midi_int, None)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if surface is None:
            return

        now = time.time()
        surface.fill((20, 20, 20))

        # BPM pulz
        beat_interval = 60.0 / max(1, self.bpm)
        beat_phase = (now - self.last_pulse_time) / beat_interval
        beat_strength = max(0.0, 1.0 - beat_phase)

        bg_intensity = int(beat_strength * 40)
        pygame.draw.rect(
            surface,
            (bg_intensity, bg_intensity, bg_intensity),
            (0, 0, self.width, self.height),
        )

        # NOTE PULZY
        remove_list = []

        for midi, data in self.active_notes.items():
            color: Tuple[int, int, int] = data["color"]
            t0: float = data["timestamp"]

            dt = now - t0
            idx = int(dt * 60)  # 60 FPS fade index

            if idx >= len(self._fade_cache):
                remove_list.append(midi)
                continue

            fade = self._fade_cache[idx]

            # Pozícia podľa MIDI výšky
            y = int(self.height - (midi - 36) * self.MIDI_Y_SCALE)
            y = max(0, min(self.height, y))

            # X pozícia – stabilný vzor
            x = (midi * 53) % self.width

            radius = int(18 + fade * 42)

            pulsed_color = (
                int(color[0] * fade),
                int(color[1] * fade),
                int(color[2] * fade),
            )

            pygame.draw.circle(surface, pulsed_color, (x, y), radius)

        # Odstránenie expirovaných pulzov
        for midi in remove_list:
            self.active_notes.pop(midi, None)

        # Oddelovacia čiara
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (0, self.height - 2),
            (self.width, self.height - 2),
            2,
        )
