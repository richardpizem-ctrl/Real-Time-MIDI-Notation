import tkinter as tk
from notation_engine.processor import NotationProcessor
from notation_engine.track_system import TrackSystem
from notation_engine.ui import (
    StaffUI,
    PianoRollUI,
    NoteVisualizerUI,
    TrackIndicatorUI
)

# PRIDANÉ – grafický renderer
from notation_engine.renderer.graphic_renderer import GraphicNotationRenderer


def main():
    # Hlavné okno
    root = tk.Tk()
    root.title("Real-Time MIDI Notation – Launcher")
    root.geometry("900x600")

    # Hlavný rám pre UI
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Inicializácia procesora a track systému
    processor = NotationProcessor()
    tracks = TrackSystem()

    # PRIDANÉ – grafický renderer
    renderer = GraphicNotationRenderer()
    processor.bind_renderer(renderer)

    # Horný panel – indikátor stopy
    track_frame = tk.Frame(main_frame)
    track_frame.pack(fill="x", pady=5)

    ui_track = TrackIndicatorUI(tracks)
    ui_track.render(track_frame)

    # Stredný panel – noty + piano roll
    center_frame = tk.Frame(main_frame)
    center_frame.pack(fill="both", expand=True)

    # Ľavá strana – notová osnova
    staff_frame = tk.Frame(center_frame)
    staff_frame.pack(side="left", fill="both", expand=True)

    ui_staff = StaffUI()
    ui_staff.render(staff_frame)

    # Pravá strana – piano roll
    piano_frame = tk.Frame(center_frame)
    piano_frame.pack(side="right", fill="both", expand=True)

    ui_piano = PianoRollUI()
    ui_piano.render(piano_frame)

    # Spodný panel – vizualizácia nôt
    bottom_frame = tk.Frame(main_frame)
    bottom_frame.pack(fill="x", pady=5)

    ui_notes = NoteVisualizerUI()
    ui_notes.render(bottom_frame)

    # Prepojenie procesora s UI
    processor.bind_tracks(tracks)
    processor.bind_visualizer(ui_notes)
    processor.bind_staff(ui_staff)
    processor.bind_piano(ui_piano)

    # Spustenie MIDI procesora
    processor.start()

    # ---------------------------------------------------
    # PRIDANÉ – slučka pre pygame renderer
    # ---------------------------------------------------
    def update_renderer():
        if renderer.is_running():
            renderer.run_event_loop_step()
            root.after(10, update_renderer)

    update_renderer()

    # Spustenie Tkinter slučky
    root.mainloop()


if __name__ == "__main__":
    main()
