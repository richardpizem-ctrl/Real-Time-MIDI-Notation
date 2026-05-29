# =========================================================
# NotationRenderer v4.3.0
# Stabilný textový renderer pre debug a fallback režim
# Optimalizovaný, bezpečný, diagnostický
# =========================================================

from typing import Callable, Optional, Dict, Any, List
import time

try:
    import pygame
except Exception:
    pygame = None


# ---------------------------------------------------------
# LIGHTWEIGHT PROFILER (shared with renderer_new)
# ---------------------------------------------------------
class RenderProfiler:
    """Ultra‑ľahký profiler pre fallback renderer."""
    def __init__(self):
        self.last_frame_ms = 0.0
        self.frame_times: List[float] = []

    def begin(self):
        self._start = time.perf_counter()

    def end(self):
        dt = (time.perf_counter() - self._start) * 1000.0
        self.last_frame_ms = dt
        self.frame_times.append(dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)


# ---------------------------------------------------------
# NOTATION RENDERER (TEXT MODE)
# ---------------------------------------------------------
class NotationRenderer:
    """
    NotationRenderer (v4.3.0)
    -------------------------
    Jednoduchý textový renderer pre real‑time MIDI pipeline.
    Poskytuje:
        - bezpečné pridávanie nôt
        - textovú vizualizáciu
        - bubnové značky (drum metadata)
        - layering (drum_layer_offset)
        - filter() funkciu
        - clear() bufferu
        - timestampy
        - FPS limit (ak pygame existuje)
        - diagnostiku (RenderProfiler)
        - ochranu pred None a nevalidnými dátami
    """

    def __init__(self):
        self.notes: List[Dict[str, Any]] = []
        self.filter_fn: Optional[Callable] = None

        # profiler
        self.profiler = RenderProfiler()

        # pygame clock je voliteľný
        try:
            if pygame is not None:
                self.clock = pygame.time.Clock()
            else:
                self.clock = None
        except Exception:
            self.clock = None

    # ---------------------------------------------------------
    # ADD NOTE
    # ---------------------------------------------------------
    def add_note(self, note: Dict[str, Any]) -> None:
        """Pridá hotovú notu do renderovacieho bufferu a vypíše ju."""
        if not isinstance(note, dict):
            print("[NotationRenderer] ⚠️ add_note: neplatný objekt:", note)
            return

        try:
            self.notes.append(note.copy())
        except Exception:
            print("[NotationRenderer] ⚠️ add_note: chyba pri kopírovaní objektu")
            return

        self.render()

    # ---------------------------------------------------------
    # CLEAR
    # ---------------------------------------------------------
    def clear(self) -> None:
        """Vymaže všetky uložené noty."""
        self.notes.clear()
        print("\n🧹 NotationRenderer: buffer vymazaný.\n")

    # ---------------------------------------------------------
    # FILTER
    # ---------------------------------------------------------
    def set_filter(self, fn: Optional[Callable]) -> None:
        """Nastaví filter funkciu."""
        if fn is None or callable(fn):
            self.filter_fn = fn
            print("[NotationRenderer] 🔎 Filter nastavený.")
        else:
            print("[NotationRenderer] ⚠️ set_filter: filter musí byť funkcia alebo None.")

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self) -> None:
        """Textová vizualizácia nôt vrátane bubnových značiek."""
        self.profiler.begin()

        timestamp = time.strftime("%H:%M:%S")
        print(f"\n--- RENDER [{timestamp}] ---")

        for n in self.notes:

            # FILTER
            if self.filter_fn is not None:
                try:
                    if not self.filter_fn(n):
                        continue
                except Exception:
                    print("[NotationRenderer] ⚠️ Filter chyba pri spracovaní noty.")
                    continue

            # ZÁKLADNÉ INFO
            try:
                base = (
                    f"pitch={n.get('pitch')}  "
                    f"dur={n.get('duration')}  "
                    f"ch={n.get('channel')}  "
                    f"bar={n.get('bar')}  "
                    f"beat={n.get('beat')}"
                )
            except Exception:
                base = "[NEPLATNÁ NOTA]"

            # DRUM INFO
            drum_info = ""
            try:
                drum = n.get("drum")
                if isinstance(drum, dict):
                    drum_info = (
                        f"   [DRUM: {drum.get('name')}, "
                        f"head={drum.get('notehead_type')}, "
                        f"stem={drum.get('stem_direction')}, "
                        f"open={drum.get('is_open_hat')}, "
                        f"closed={drum.get('is_closed_hat')}, "
                        f"ghost={drum.get('is_ghost')}, "
                        f"accent={drum.get('is_accent')}]"
                    )
            except Exception:
                drum_info = "   [DRUM: ERROR]"

            # LAYER OFFSET
            layer = ""
            try:
                if "drum_layer_offset" in n:
                    layer = f"   layer_offset={n['drum_layer_offset']}"
            except Exception:
                layer = ""

            print(base + drum_info + layer)

        print("--------------\n")

        # FPS limit (ak pygame existuje)
        try:
            if self.clock:
                self.clock.tick(60)
        except Exception:
            pass

        self.profiler.end()
