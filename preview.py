# =========================================================
# preview.py – Real-Time MIDI Notation v4.3.0
# Stable renderer preview (Tkinter)
# =========================================================

import tkinter as tk
from notation_engine.notation_renderer import NotationRenderer
from core.logger import Logger


def build_demo_timeline():
    """
    Build a demo timeline for renderer preview.
    Real‑time safe: no exceptions allowed.
    """
    try:
        timeline = []

        # Barline + chord
        timeline.append({
            "type": "barline",
            "start": 0.0,
            "chord": "Cmaj7"
        })

        # Melody
        timeline.append({
            "type": "note",
            "track_type": "melody",
            "pitch": 72,
            "start": 0.0,
            "duration": 0.5,
            "color": "#FFFFFF",
        })
        timeline.append({
            "type": "note",
            "track_type": "melody",
            "pitch": 74,
            "start": 0.5,
            "duration": 0.5,
            "color": "#FFFFFF",
        })

        # Bass
        timeline.append({
            "type": "note",
            "track_type": "bass",
            "pitch": 48,
            "start": 0.0,
            "duration": 1.0,
            "color": "#FFFFFF",
        })

        # Drums
        timeline.append({
            "type": "note",
            "track_type": "drums",
            "pitch": 36,
            "start": 0.0,
            "duration": 0.25,
            "color": "#FFFFFF",
        })
        timeline.append({
            "type": "note",
            "track_type": "drums",
            "pitch": 38,
            "start": 0.5,
            "duration": 0.25,
            "color": "#FFFFFF",
        })

        return timeline

    except Exception:
        try:
            Logger.error("Preview timeline build failure")
        except Exception:
            pass
        return []


def main():
    Logger.info("=== PREVIEW MODE v4.3.0 ===")

    try:
        root = tk.Tk()
        root.title("Real-Time MIDI Notation – Preview v4.3.0")

        canvas = tk.Canvas(root, width=1200, height=400, bg="#202020")
        canvas.pack(fill="both", expand=True)

        # Renderer
        renderer = NotationRenderer(canvas=canvas)

        # Demo timeline
        timeline = build_demo_timeline()

        # Dummy chord object (renderer expects .name)
        class DummyChord:
            def __init__(self, name):
                self.name = name

        current_chord = DummyChord("Cmaj7")

        # Render
        try:
            renderer.render(timeline, current_chord=current_chord)
        except Exception:
            try:
                Logger.error("Preview render failure")
            except Exception:
                pass

        root.mainloop()

    except Exception:
        try:
            Logger.error("Preview initialization failure")
        except Exception:
            pass


if __name__ == "__main__":
    main()
