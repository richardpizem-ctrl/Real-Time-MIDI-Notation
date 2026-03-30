import tkinter as tk


class CanvasUI:
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, bg="white", width=1100, height=700)
        self.canvas.pack(fill="both", expand=True)

    def get_canvas(self):
        return self.canvas
