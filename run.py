import tkinter as tk
from notation_engine.processor import NotationProcessor
from notation_engine.track_system import TrackSystem
from notation_engine.ui import StaffUI, PianoRollUI, NoteVisualizerUI, TrackIndicatorUI

def main():
    root = tk.Tk()
    root.title("Real-Time MIDI Notation – Launcher")
    root.geometry("300x150")

    tk.Label(root, text="UI sa spúšťa...", font=("Arial", 14)).pack(pady=20)

    processor = NotationProcessor()
    tracks = TrackSystem()

    ui_track = TrackIndicatorUI(tracks)
    ui_notes = NoteVisualizerUI()
    ui_staff = StaffUI()
    ui_piano = PianoRollUI()

    root.mainloop()

if __name__ == "__main__":
    main()
