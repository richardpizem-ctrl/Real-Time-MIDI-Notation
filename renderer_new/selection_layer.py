# =========================================================
# SelectionLayer v2.0.0
# Stabilná overlay vrstva pre výber nôt (selection box + highlight)
# =========================================================

import pygame
from typing import List, Tuple, Optional
from .layers import BaseLayer


class SelectionLayer(BaseLayer):
    """
    SelectionLayer (v2.0.0)
    -----------------------
    - Výber nôt pomocou selection boxu
    - Highlight vybraných nôt
    - Nezasahuje do NotesLayer (čistý overlay)
    - Real‑time safe
    - Pripravené na v3 (AI/TIMELINE editácia)
    """

    def __init__(self, controller, z_index: int = 4):
        super().__init__(z_index=z_index, visible=True)

        self.controller = controller

        # Selection state
        self.is_selecting = False
        self.start_pos: Optional[Tuple[int, int]] = None
        self.current_pos: Optional[Tuple[int, int]] = None

        # Výsledok výberu
        self.selected_notes: List[int] = []

        # Cache pre selection box
        self._box_surface = None

    # ---------------------------------------------------------
    # INPUT EVENTS
    # ---------------------------------------------------------
    def on_mouse_down(self, x: int, y: int):
        try:
            self.is_selecting = True
            self.start_pos = (x, y)
            self.current_pos = (x, y)
        except Exception:
            pass

    def on_mouse_drag(self, x: int, y: int):
        if self.is_selecting:
            try:
                self.current_pos = (x, y)
            except Exception:
                pass

    def on_mouse_up(self, x: int, y: int, notes: List[dict]):
        if not self.is_selecting:
            return

        try:
            self.current_pos = (x, y)
            self.is_selecting = False
        except Exception:
            return

        rect = self._get_selection_rect()
        if rect is None:
            return

        sx, sy, sw, sh = rect
        sel_rect = pygame.Rect(sx, sy, sw, sh)

        self.selected_notes.clear()

        # Hit-test
        for i, note in enumerate(notes):
            try:
                nx = note.get("x")
                ny = note.get("y")
                nw = note.get("width", 8)
                nh = note.get("height", 8)

                if nx is None or ny is None:
                    continue

                if sel_rect.colliderect(pygame.Rect(nx, ny, nw, nh)):
                    self.selected_notes.append(i)

            except Exception:
                continue

    # ---------------------------------------------------------
    # SELECTION RECT
    # ---------------------------------------------------------
    def _get_selection_rect(self) -> Optional[Tuple[int, int, int, int]]:
        if not self.start_pos or not self.current_pos:
            return None

        try:
            x1, y1 = self.start_pos
            x2, y2 = self.current_pos

            sx = min(x1, x2)
            sy = min(y1, y2)
            sw = abs(x2 - x1)
            sh = abs(y2 - y1)

            return (sx, sy, sw, sh)
        except Exception:
            return None

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def get_selected_notes(self) -> List[int]:
        return list(self.selected_notes)

    def clear_selection(self):
        self.selected_notes.clear()

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if surface is None:
            return

        # 1. Selection box
        if self.is_selecting and self.start_pos and self.current_pos:
            rect = self._get_selection_rect()
            if rect:
                sx, sy, sw, sh = rect

                try:
                    # Polopriesvitný overlay
                    box = pygame.Surface((sw, sh), pygame.SRCALPHA)
                    box.fill((0, 180, 255, 40))
                    surface.blit(box, (sx, sy))

                    # Obrys
                    pygame.draw.rect(surface, (0, 180, 255), (sx, sy, sw, sh), 1)
                except Exception:
                    pass

        # 2. Highlight vybraných nôt
        try:
            notes = getattr(self.controller, "notes", None)
            if not notes:
                return

            for i in self.selected_notes:
                try:
                    note = notes[i]
                    nx = note.get("x")
                    ny = note.get("y")
                    nw = note.get("width", 8)
                    nh = note.get("height", 8)

                    if nx is None or ny is None:
                        continue

                    pygame.draw.rect(surface, (0, 255, 180), (nx, ny, nw, nh), 2)

                except Exception:
                    continue

        except Exception:
            pass
