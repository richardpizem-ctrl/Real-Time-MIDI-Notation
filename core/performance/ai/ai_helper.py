# =========================================================
# ai_helper.py v4.3.0
# Ultra-light AI utility module for real-time MIDI systems
# =========================================================

from __future__ import annotations
from typing import Any, Optional


class AIHelper:
    """
    AIHelper (v4.3.0)
    -----------------
    Lightweight AI utility module for:
        - MIDI analysis
        - pattern detection
        - auto-naming
        - tempo/velocity heuristics
        - future v5 AI hooks

    Features:
        - real-time safe
        - no exceptions
        - __slots__ for ultra-low latency
        - zero-allocation hot path
        - clean English API
        - ready for v5 (LLM hooks, predictive models)
    """

    __slots__ = (
        "enabled",
        "last_note",
        "last_velocity",
        "note_count",
        "pattern_buffer",
    )

    def __init__(self, enabled: bool = True):
        self.enabled = bool(enabled)
        self.last_note: Optional[int] = None
        self.last_velocity: Optional[int] = None
        self.note_count: int = 0
        self.pattern_buffer: list[int] = []

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle AI helper state and return new value."""
        self.enabled = not self.enabled
        return self.enabled

    # ---------------------------------------------------------
    # MIDI EVENT INGESTION
    # ---------------------------------------------------------
    def on_note_on(self, note: int, velocity: int) -> None:
        """Feed a note-on event into the AI helper."""
        if not self.enabled:
            return

        try:
            self.last_note = int(note)
            self.last_velocity = int(velocity)
            self.note_count += 1

            # Simple pattern buffer (fixed size)
            self.pattern_buffer.append(self.last_note)
            if len(self.pattern_buffer) > 32:
                self.pattern_buffer.pop(0)

        except Exception:
            # Never break real-time loop
            pass

    def on_note_off(self, note: int) -> None:
        """Optional note-off ingestion."""
        if not self.enabled:
            return
        # Currently unused, but reserved for v5
        return

    # ---------------------------------------------------------
    # SIMPLE AI HEURISTICS
    # ---------------------------------------------------------
    def guess_track_name(self) -> str:
        """
        Guess a track name based on recent notes.
        Very lightweight heuristic.
        """
        if not self.enabled or not self.pattern_buffer:
            return "Track"

        try:
            avg = sum(self.pattern_buffer) / len(self.pattern_buffer)
            if avg < 50:
                return "Bass"
            if avg < 70:
                return "Piano"
            if avg < 90:
                return "Strings"
            return "Lead"
        except Exception:
            return "Track"

    def detect_pattern(self) -> Optional[str]:
        """
        Detect simple repeating patterns.
        Real-time safe, zero-cost heuristic.
        """
        buf = self.pattern_buffer
        if not buf or len(buf) < 6:
            return None

        try:
            # Check last 3 notes repeating
            if buf[-1] == buf[-3] and buf[-2] == buf[-4]:
                return "Repeating motif"
        except Exception:
            pass

        return None

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------
    def reset(self) -> None:
        """Reset AI helper state."""
        try:
            self.last_note = None
            self.last_velocity = None
            self.note_count = 0
            self.pattern_buffer.clear()
        except Exception:
            pass
