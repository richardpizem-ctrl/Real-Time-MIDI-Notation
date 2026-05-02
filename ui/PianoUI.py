# =========================================================
# PianoUI v2.0.0
# Stabilná real‑time klavírna vizualizácia
# =========================================================

import pygame
import time


class PianoUI:
    """
    PianoUI (v2.0.0)
    ----------------
    Real‑time klavírna vizualizácia s podporou:
        - velocity‑based farieb
        - poly‑aftertouch
        - NOTE‑ON flash animácie
        - LED / gradient štýlu kláves
    Pripravené na v3:
        - RGB pulsing
        - MPE X/Y/Z
        - vibrato waveform
        - 3D key‑press efekt
    """

    WHITE_KEY_WIDTH = 22
    WHITE_KEY_HEIGHT = 140
    BLACK_KEY_WIDTH = 14
    BLACK_KEY_HEIGHT = 90

    FIRST_MIDI_NOTE = 36
    LAST_MIDI_NOTE = 96

    def __init__(self, width: int = 1500, height: int = 180):
        self.width = width
        self.height = height

        # Aktívne klávesy: midi → {"color": (r,g,b), "velocity": v, "aftertouch": a, "time": t}
        self.active_keys: dict[int, dict] = {}

        # Prepočítané pozície kláves
        self.white_keys: list[tuple[int, pygame.Rect]] = []
        self.black_keys: list[tuple[int, pygame.Rect]] = []

        # Cache pre gradienty (optimalizácia)
        self._white_gradient: pygame.Surface | None = None
        self._black_shine: pygame.Surface | None = None

        self._calculate_positions()
        self._build_gradients()

    # ---------------------------------------------------------
    # CALCULATE KEY POSITIONS
    # ---------------------------------------------------------
    def _calculate_positions(self) -> None:
        white_order = [0, 2, 4, 5, 7, 9, 11]
        black_offsets = {1: 0.65, 3: 1.65, 6: 3.65, 8: 4.65, 10: 5.65}

        self.white_keys.clear()
        self.black_keys.clear()

        white_index = 0

        # WHITE KEYS
        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi % 12
            if note in white_order:
                x = white_index * self.WHITE_KEY_WIDTH
                rect = pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)
                self.white_keys.append((midi, rect))
                white_index += 1

        # BLACK KEYS
        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi % 12
            if note in black_offsets:
                octave = (midi - self.FIRST_MIDI_NOTE) // 12
                base = octave * 7
                x = int((base + black_offsets[note]) * self.WHITE_KEY_WIDTH)
                rect = pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)
                self.black_keys.append((midi, rect))

    # ---------------------------------------------------------
    # GRADIENT CACHE
    # ---------------------------------------------------------
    def _build_gradients(self) -> None:
        """Predvygeneruje gradienty pre biele a čierne klávesy (optimalizácia)."""
        # White key gradient
        try:
            grad = pygame.Surface(
                (self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT), pygame.SRCALPHA
            )
            for y in range(self.WHITE_KEY_HEIGHT):
                alpha = int(80 * (1 - y / self.WHITE_KEY_HEIGHT))
                pygame.draw.line(
                    grad, (255, 255, 255, alpha), (0, y), (self.WHITE_KEY_WIDTH, y)
                )
            self._white_gradient = grad
        except Exception:
            self._white_gradient = None

        # Black key shine
        try:
            shine = pygame.Surface(
                (self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT), pygame.SRCALPHA
            )
            for y in range(self.BLACK_KEY_HEIGHT):
                alpha = int(120 * (1 - y / self.BLACK_KEY_HEIGHT))
                pygame.draw.line(
                    shine, (255, 255, 255, alpha), (0, y), (self.BLACK_KEY_WIDTH, y)
                )
            self._black_shine = shine
        except Exception:
            self._black_shine = None

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _velocity_color(self, velocity: int) -> tuple[int, int, int]:
        """Map velocity 0–127 → farba."""
        v = max(0, min(127, int(velocity)))
        return (
            int(80 + v * 1.3),   # R
            int(40 + v * 0.6),   # G
            int(40 + v * 0.3),   # B
        )

    def _aftertouch_boost(self, base_color: tuple[int, int, int], aftertouch: int) -> tuple[int, int, int]:
        """Zvýraznenie farby podľa poly‑aftertouch."""
        a = max(0, min(127, int(aftertouch)))
        boost = int(a * 0.8)
        r = min(255, base_color[0] + boost)
        g = min(255, base_color[1] + boost // 2)
        b = min(255, base_color[2] + boost // 3)
        return (r, g, b)

    def _note_on_animation(self, t0: float) -> float:
        """Vracia multiplikátor jasu podľa času od NOTE ON."""
        dt = time.time() - t0
        if dt < 0.12:
            return 1.0 + (0.5 * (1 - dt / 0.12))  # krátky flash
        return 1.0

    # ---------------------------------------------------------
    # HIGHLIGHT / UNHIGHLIGHT
    # ---------------------------------------------------------
    def highlight_key(self, midi_note: int, velocity: int = 100, aftertouch: int = 0) -> None:
        """NOTE ON – zvýrazní klávesu s velocity a aftertouch."""
        if midi_note is None:
            return

        base_color = self._velocity_color(velocity)
        boosted = self._aftertouch_boost(base_color, aftertouch)

        self.active_keys[int(midi_note)] = {
            "color": boosted,
            "velocity": int(velocity),
            "aftertouch": int(aftertouch),
            "time": time.time(),
        }

    def update_aftertouch(self, midi_note: int, aftertouch: int) -> None:
        """Poly‑aftertouch update."""
        key = int(midi_note)
        if key in self.active_keys:
            info = self.active_keys[key]
            base = self._velocity_color(info["velocity"])
            info["aftertouch"] = int(aftertouch)
            info["color"] = self._aftertouch_boost(base, aftertouch)

    def unhighlight_key(self, midi_note: int) -> None:
        """NOTE OFF."""
        key = int(midi_note) if midi_note is not None else None
        if key in self.active_keys:
            del self.active_keys[key]

    def clear(self) -> None:
        self.active_keys.clear()

    def reset(self) -> None:
        self.clear()
        self._calculate_positions()
        self._build_gradients()

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        if surface is None:
            return

        surface.fill((20, 20, 20))

        # WHITE KEYS
        for midi, rect in self.white_keys:
            if midi in self.active_keys:
                info = self.active_keys[midi]
                color = info["color"]

                # NOTE ON animácia
                flash = self._note_on_animation(info["time"])
                color = (
                    min(255, int(color[0] * flash)),
                    min(255, int(color[1] * flash)),
                    min(255, int(color[2] * flash)),
                )

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)

                if self._white_gradient is not None:
                    surface.blit(self._white_gradient, rect.topleft)
            else:
                pygame.draw.rect(surface, (255, 255, 255), rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        # BLACK KEYS
        for midi, rect in self.black_keys:
            if midi in self.active_keys:
                info = self.active_keys[midi]
                color = info["color"]

                flash = self._note_on_animation(info["time"])
                color = (
                    min(255, int(color[0] * flash)),
                    min(255, int(color[1] * flash)),
                    min(255, int(color[2] * flash)),
                )

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (30, 30, 30), rect, 1)

                if self._black_shine is not None:
                    surface.blit(self._black_shine, rect.topleft)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect)
                pygame.draw.rect(surface, (40, 40, 40), rect, 1)
