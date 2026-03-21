# preview.py

import tkinter as tk
from notation_engine.notation_renderer import NotationRenderer


def build_demo_timeline():
    """
    Demo timeline pre vizuálny náhľad.
    """
    timeline = []

    # Takt 1 – barline + akord
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


def main():
    root = tk.Tk()
    root.title("Real-Time MIDI Notation – Preview")

    canvas = tk.Canvas(root, width=1200, height=400, bg="#202020")
    canvas.pack(fill="both", expand=True)

    renderer = NotationRenderer(canvas=canvas)

    timeline = build_demo_timeline()

    class DummyChord:
        def __init__(self, name):
            self.name = name

    current_chord = DummyChord("Cmaj7")

    renderer.render(timeline, current_chord=current_chord)

    root.mainloop()


if __name__ == "__main__":
    main()
