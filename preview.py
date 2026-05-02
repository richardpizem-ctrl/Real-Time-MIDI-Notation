# =========================================================
# preview.py – Real-Time MIDI Notation v2.0.0
# Stabilný vizuálny náhľad renderera (Tkinter)
# =========================================================

import tkinter as tk
from notation_engine.notation_renderer import NotationRenderer
from core.logger import Logger


def build_demo_timeline():
    """
    Demo timeline pre vizuálny náhľad renderera.
    Real‑time safe: žiadne výnimky nesmú preraziť.
    """
    try:
        timeline = []

        # -----------------------------------------------------
        # Takt 1 – barline + akord
        # -----------------------------------------------------
        timeline.append({
            "type": "barline",
            "start": 0.0,
            "chord": "Cmaj7"
        })

        # -----------------------------------------------------
        # Melody (horná linka)
        # -----------------------------------------------------
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

        # -----------------------------------------------------
        # Bass (spodná linka)
        # -----------------------------------------------------
        timeline.append({
            "type": "note",
            "track_type": "bass",
            "pitch": 48,
            "start": 0.0,
            "duration": 1.0,
            "color": "#FFFFFF",
        })

        # -----------------------------------------------------
        # Drums (perkusie)
        # -----------------------------------------------------
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

    except Exception as e:
        Logger.error(f"Preview timeline build error: {e}")
        return []


def main():
    Logger.info("=== PREVIEW MODE v2.0.0 ===")

    try:
        root = tk.Tk()
        root.title("Real-Time MIDI Notation – Preview v2.0.0")

        canvas = tk.Canvas(root, width=1200, height=400, bg="#202020")
        canvas.pack(fill="both", expand=True)

        # Renderer
        renderer = NotationRenderer(canvas=canvas)

        # Demo timeline
        timeline = build_demo_timeline()

        # Dummy akord objekt (renderer očakáva .name)
        class DummyChord:
            def __init__(self, name):
                self.name = name

        current_chord = DummyChord("Cmaj7")

        # Render
        try:
            renderer.render(timeline, current_chord=current_chord)
        except Exception as e:
            Logger.error(f"Preview render error: {e}")

        root.mainloop()

    except Exception as e:
        Logger.error(f"Preview initialization error: {e}")


if __name__ == "__main__":
    main()
