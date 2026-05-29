# =========================================================
# PianoUI v4.3.0
# Ultra‑optimalizovaná real‑time klavírna vizualizácia
# =========================================================

import pygame
import time


class PianoUI:
    """
    PianoUI (v4.3.0)
    ----------------
    Real‑time klavírna vizualizácia s podporou:
        - velocity‑based farieb (predpočítané)
        - poly‑aftertouch (rýchle boostovanie)
        - NOTE‑ON flash animácie (konštantný čas)
        - LED / gradient štýlu kláves (cache)
        - stabilné výpočty pozícií (prepočítané len pri resete)
        - ultra‑nízka latencia (žiadne zbytočné výpočty v draw())

    Pripravené na v5:
        - RGB pulsing
        - MPE X/Y/Z
        - vibrato waveform
        - 3D key‑press efekt
    """

    __slots__ = (
        "width", "height",
        "active_keys",
        "white_keys", "black_keys",
        "_white_gradient", "_black_shine",
        "_velocity_cache",
    )

    WHITE_KEY_WIDTH = 22
    WHITE_KEY_HEIGHT = 140
    BLACK_KEY_WIDTH = 14
    BLACK_KEY_HEIGHT = 90

    FIRST_MIDI_NOTE = 36
    LAST_MIDI_NOTE = 96

    FLASH_TIME = 0.12

    # ---------------------------------------------------------
    # INIT
    # ---------------------------------------------------------
    def __init__(self, width: int = 1500, height: int = 180):
        self.width = int(width)
        self.height = int(height)

        self.active_keys: dict[int, dict] = {}

        self.white_keys = []
        self.black_keys = []

        self._white_gradient = None
        self._black_shine = None

        # Predpočítané velocity farby (0–127)
        self._velocity_cache = [
            (
                int(80 + v * 1.3),
                int(40 + v * 0.6),
                int(40 + v * 0.3),
            )
            for v in range(128)
        ]

        self._calculate_positions()
        self._build_gradients()

    # ---------------------------------------------------------
    # CALCULATE KEY POSITIONS
    # ---------------------------------------------------------
    def _calculate_positions(self) -> None:
        white_order = {0, 2, 4, 5, 7, 9, 11}
        black_offsets = {1: 0.65, 3: 1.65, 6: 3.65, 8: 4.65, 10: 5.65}

        self.white_keys.clear()
        self.black_keys.clear()

        white_index = 0

        # WHITE KEYS
        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            if (midi % 12) in white_order:
                x = white_index * self.WHITE_KEY_WIDTH
                self.white_keys.append((midi, pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)))
                white_index += 1

        # BLACK KEYS
        for midi in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi % 12
            if note in black_offsets:
                octave = (midi - self.FIRST_MIDI_NOTE) // 12
                base = octave * 7
                x = int((base + black_offsets[note]) * self.WHITE_KEY_WIDTH)
                self.black_keys.append((midi, pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)))

    # ---------------------------------------------------------
    # GRADIENT CACHE
    # ---------------------------------------------------------
    def _build_gradients(self) -> None:
        # White key gradient
        try:
            grad = pygame.Surface((self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT), pygame.SRCALPHA)
            for y in range(self.WHITE_KEY_HEIGHT):
                alpha = int(80 * (1 - y / self.WHITE_KEY_HEIGHT))
                pygame.draw.line(grad, (255, 255, 255, alpha), (0, y), (self.WHITE_KEY_WIDTH, y))
            self._white_gradient = grad
        except Exception:
            self._white_gradient = None

        # Black key shine
        try:
            shine = pygame.Surface((self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT), pygame.SRCALPHA)
            for y in range(self.BLACK_KEY_HEIGHT):
                alpha = int(120 * (1 - y / self.BLACK_KEY_HEIGHT))
                pygame.draw.line(shine, (255, 255, 255, alpha), (0, y), (self.BLACK_KEY_WIDTH, y))
            self._black_shine = shine
        except Exception:
            self._black_shine = None

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _velocity_color(self, velocity: int):
        return self._velocity_cache[max(0, min(127, int(velocity)))]

    def _aftertouch_boost(self, base_color, aftertouch: int):
        a = max(0, min(127, int(aftertouch)))
        boost = int(a * 0.8)
        return (
            min(255, base_color[0] + boost),
            min(255, base_color[1] + boost // 2),
            min(255, base_color[2] + boost // 3),
        )

    def _flash_multiplier(self, t0: float) -> float:
        dt = time.time() - t0
        if dt < self.FLASH_TIME:
            return 1.0 + (0.5 * (1 - dt / self.FLASH_TIME))
        return 1.0

    # ---------------------------------------------------------
    # KEY STATE
    # ---------------------------------------------------------
    def highlight_key(self, midi_note: int, velocity: int = 100, aftertouch: int = 0):
        if midi_note is None:
            return

        base = self._velocity_color(velocity)
        boosted = self._aftertouch_boost(base, aftertouch)

        self.active_keys[int(midi_note)] = {
            "color": boosted,
            "velocity": int(velocity),
            "aftertouch": int(aftertouch),
            "time": time.time(),
        }

    def update_aftertouch(self, midi_note: int, aftertouch: int):
        key = int(midi_note)
        if key in self.active_keys:
            info = self.active_keys[key]
            base = self._velocity_color(info["velocity"])
            info["aftertouch"] = int(aftertouch)
            info["color"] = self._aftertouch_boost(base, aftertouch)

    def unhighlight_key(self, midi_note: int):
        key = int(midi_note)
        self.active_keys.pop(key, None)

    def clear(self):
        self.active_keys.clear()

    def reset(self):
        self.clear()
        self._calculate_positions()
        self._build_gradients()

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if surface is None:
            return

        surface.fill((20, 20, 20))

        # WHITE KEYS
        for midi, rect in self.white_keys:
            info = self.active_keys.get(midi)
            if info:
                color = info["color"]
                flash = self._flash_multiplier(info["time"])
                color = (
                    min(255, int(color[0] * flash)),
                    min(255, int(color[1] * flash)),
                    min(255, int(color[2] * flash)),
                )
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (255, 255, 255), rect)

            pygame.draw.rect(surface, (0, 0, 0), rect, 2)
            if self._white_gradient:
                surface.blit(self._white_gradient, rect.topleft)

        # BLACK KEYS
        for midi, rect in self.black_keys:
            info = self.active_keys.get(midi)
            if info:
                color = info["color"]
                flash = self._flash_multiplier(info["time"])
                color = (
                    min(255, int(color[0] * flash)),
                    min(255, int(color[1] * flash)),
                    min(255, int(color[2] * flash)),
                )
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect)

            pygame.draw.rect(surface, (40, 40, 40), rect, 1)
            if self._black_shine:
                surface.blit(self._black_shine, rect.topleft)
