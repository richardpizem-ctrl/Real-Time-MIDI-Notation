"""
PianoUI – Real‑Time Klavírna Vizualizácia (FÁZA 4+)

Rozšírené o:
- velocity‑based farby
- poly‑aftertouch vizualizáciu
- animácie pri NOTE ON
- LED / gradient štýl kláves
"""

import pygame
import math
import time


class PianoUI:
    WHITE_KEY_WIDTH = 22
    WHITE_KEY_HEIGHT = 140
    BLACK_KEY_WIDTH = 14
    BLACK_KEY_HEIGHT = 90

    FIRST_MIDI_NOTE = 36
    LAST_MIDI_NOTE = 96

    def __init__(self, width=1500, height=180):
        self.width = width
        self.height = height

        # Aktívne klávesy: midi → {"color": (r,g,b), "velocity": v, "aftertouch": a, "time": t}
        self.active_keys = {}

        # Prepočítané pozície kláves
        self.white_keys = []
        self.black_keys = []

        self._calculate_positions()

    # ---------------------------------------------------------
    # CALCULATE KEY POSITIONS
    # ---------------------------------------------------------
    def _calculate_positions(self):
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
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _velocity_color(self, velocity):
        """Map velocity 0–127 → farba."""
        v = max(0, min(127, velocity))
        return (
            int(80 + v * 1.3),   # R
            int(40 + v * 0.6),   # G
            int(40 + v * 0.3),   # B
        )

    def _aftertouch_boost(self, base_color, aftertouch):
        """Zvýraznenie farby podľa poly‑aftertouch."""
        a = max(0, min(127, aftertouch))
        boost = int(a * 0.8)
        r = min(255, base_color[0] + boost)
        g = min(255, base_color[1] + boost // 2)
        b = min(255, base_color[2] + boost // 3)
        return (r, g, b)

    def _note_on_animation(self, t0):
        """Vracia multiplikátor jasu podľa času od NOTE ON."""
        dt = time.time() - t0
        if dt < 0.12:
            return 1.0 + (0.5 * (1 - dt / 0.12))  # krátky flash
        return 1.0

    # ---------------------------------------------------------
    # HIGHLIGHT / UNHIGHLIGHT
    # ---------------------------------------------------------
    def highlight_key(self, midi_note, velocity=100, aftertouch=0):
        """NOTE ON – zvýrazní klávesu s velocity a aftertouch."""
        if midi_note is None:
            return

        base_color = self._velocity_color(velocity)
        boosted = self._aftertouch_boost(base_color, aftertouch)

        self.active_keys[midi_note] = {
            "color": boosted,
            "velocity": velocity,
            "aftertouch": aftertouch,
            "time": time.time(),
        }

    def update_aftertouch(self, midi_note, aftertouch):
        """Poly‑aftertouch update."""
        if midi_note in self.active_keys:
            info = self.active_keys[midi_note]
            base = self._velocity_color(info["velocity"])
            info["aftertouch"] = aftertouch
            info["color"] = self._aftertouch_boost(base, aftertouch)

    def unhighlight_key(self, midi_note):
        """NOTE OFF."""
        if midi_note in self.active_keys:
            del self.active_keys[midi_note]

    def clear(self):
        self.active_keys.clear()

    def reset(self):
        self.clear()
        self._calculate_positions()

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
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

                # LED gradient
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)

                # gradient overlay
                grad = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                for y in range(rect.h):
                    alpha = int(80 * (1 - y / rect.h))
                    pygame.draw.line(grad, (255, 255, 255, alpha), (0, y), (rect.w, y))
                surface.blit(grad, rect.topleft)

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

                # LED shine
                shine = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                for y in range(rect.h):
                    alpha = int(120 * (1 - y / rect.h))
                    pygame.draw.line(shine, (255, 255, 255, alpha), (0, y), (rect.w, y))
                surface.blit(shine, rect.topleft)

            else:
                pygame.draw.rect(surface, (0, 0, 0), rect)
                pygame.draw.rect(surface, (40, 40, 40), rect, 1)
