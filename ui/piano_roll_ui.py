# =========================================================
# PianoRollUI v4.3.0
# Ultra‑optimalizovaná real‑time klavírna vizualizácia (pygame)
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import pygame
import time
from typing import Dict, Tuple, List, Any


class PianoRollUI:
    __slots__ = (
        "width", "height",
        "active_keys",
        "white_keys", "black_keys",
        "font",
        "_fade_cache_white",
        "_fade_cache_black",
    )

    WHITE_KEY_WIDTH = 20
    WHITE_KEY_HEIGHT = 120
    BLACK_KEY_WIDTH = 12
    BLACK_KEY_HEIGHT = 80

    FIRST_MIDI_NOTE = 36   # C2
    LAST_MIDI_NOTE = 96    # C7

    FADE_SPEED = 1.35

    def __init__(self, width: int = 1400, height: int = 200):
        self.width = int(width)
        self.height = int(height)

        # midi_note -> (color, timestamp)
        self.active_keys: Dict[int, Tuple[Tuple[int, int, int], float]] = {}

        self.white_keys: List[Tuple[int, pygame.Rect]] = []
        self.black_keys: List[Tuple[int, pygame.Rect]] = []

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 12, bold=True)
        except Exception:
            self.font = None

        # predpočítané fade hodnoty (0–2s pri ~60 FPS)
        self._fade_cache_white = [
            max(0.0, 1.0 - (i / 120.0) * self.FADE_SPEED)
            for i in range(240)
        ]
        self._fade_cache_black = self._fade_cache_white  # rovnaká krivka

        self._calculate_key_positions()

    # ---------------------------------------------------------
    # PUBLIC API (UIManager-safe)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return

    # ---------------------------------------------------------
    # CALCULATE KEY POSITIONS
    # ---------------------------------------------------------
    def _calculate_key_positions(self):
        white_key_order = [0, 2, 4, 5, 7, 9, 11]
        black_key_offsets = {1: 0.65, 3: 1.65, 6: 3.65, 8: 4.65, 10: 5.65}

        white_index = 0
        self.white_keys.clear()
        self.black_keys.clear()

        # WHITE KEYS
        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            if (midi_note % 12) in white_key_order:
                x = white_index * self.WHITE_KEY_WIDTH
                rect = pygame.Rect(x, 0, self.WHITE_KEY_WIDTH, self.WHITE_KEY_HEIGHT)
                self.white_keys.append((midi_note, rect))
                white_index += 1

        # BLACK KEYS
        for midi_note in range(self.FIRST_MIDI_NOTE, self.LAST_MIDI_NOTE + 1):
            note = midi_note % 12
            if note in black_key_offsets:
                octave = (midi_note - self.FIRST_MIDI_NOTE) // 12
                base_white_index = octave * 7
                x = int((base_white_index + black_key_offsets[note]) * self.WHITE_KEY_WIDTH)
                rect = pygame.Rect(x, 0, self.BLACK_KEY_WIDTH, self.BLACK_KEY_HEIGHT)
                self.black_keys.append((midi_note, rect))

    # ---------------------------------------------------------
    # KEY HIGHLIGHT
    # ---------------------------------------------------------
    def highlight_key(self, midi_note: Any, color=(255, 80, 80)):
        """Highlight a key with fade-out animation."""
        if midi_note is None:
            return

        try:
            midi = int(midi_note)
        except Exception:
            return

        if not isinstance(color, (tuple, list)) or len(color) != 3:
            color = (255, 80, 80)

        self.active_keys[midi] = (tuple(color), time.time())

    def unhighlight_key(self, midi_note: Any):
        try:
            midi = int(midi_note)
        except Exception:
            return

        self.active_keys.pop(midi, None)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if surface is None:
            return

        surface.fill((30, 30, 30))
        now = time.time()

        # --- WHITE KEYS ---
        for midi_note, rect in self.white_keys:
            base_color = (255, 255, 255)
            color = base_color

            data = self.active_keys.get(midi_note)
            if data is not None:
                key_color, t = data
                dt = now - t
                idx = int(dt * 60)  # ~60 FPS index

                if idx < len(self._fade_cache_white):
                    fade = self._fade_cache_white[idx]
                    inv = 1.0 - fade
                    color = (
                        int(key_color[0] * fade + base_color[0] * inv),
                        int(key_color[1] * fade + base_color[1] * inv),
                        int(key_color[2] * fade + base_color[2] * inv),
                    )
                else:
                    # pulz skončil
                    self.active_keys.pop(midi_note, None)

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        # --- BLACK KEYS ---
        for midi_note, rect in self.black_keys:
            base_color = (0, 0, 0)
            color = base_color

            data = self.active_keys.get(midi_note)
            if data is not None:
                key_color, t = data
                dt = now - t
                idx = int(dt * 60)

                if idx < len(self._fade_cache_black):
                    fade = self._fade_cache_black[idx]
                    color = (
                        int(key_color[0] * fade),
                        int(key_color[1] * fade),
                        int(key_color[2] * fade),
                    )
                else:
                    self.active_keys.pop(midi_note, None)

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (50, 50, 50), rect, 1)

        # --- OCTAVE LABELS ---
        if self.font:
            for midi_note, rect in self.white_keys:
                if midi_note % 12 == 0:  # C note
                    octave = midi_note // 12 - 1
                    label = f"C{octave}"
                    text = self.font.render(label, True, (0, 0, 0))
                    surface.blit(text, (rect.x + 2, rect.y + self.WHITE_KEY_HEIGHT - 18))

        # --- HORIZONTAL SEPARATOR ---
        h = surface.get_height()
        pygame.draw.line(
            surface,
            (80, 80, 80),
            (0, h - 2),
            (self.width, h - 2),
            2,
        )
