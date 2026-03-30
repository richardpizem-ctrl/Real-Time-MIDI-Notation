import tkinter as tk
from ui_manager import UIManager


class UIWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Real-Time MIDI Notation")
        self.root.geometry("1200x800")

        self.ui = UIManager(self.root)
        self.ui.build_layout()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    window = UIWindow()
    window.run()
